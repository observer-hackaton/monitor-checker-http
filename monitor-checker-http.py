#!/usr/bin/env python
import pika
import json
import requests
import os

RABBIT_MQ_SERVER = os.environ["RABBIT_MQ_SERVER"]
RABBIT_MQ_USER = os.environ["RABBIT_MQ_USER"]
RABBIT_MQ_PWD = os.environ["RABBIT_MQ_PWD"]

credentials = pika.PlainCredentials(RABBIT_MQ_USER, RABBIT_MQ_PWD)

connection = pika.BlockingConnection(pika.ConnectionParameters(
               RABBIT_MQ_SERVER, credentials = credentials))
channel = connection.channel()

def callback(ch, method, properties, body):
    req = json.loads(body)
    host = json.loads(req["monitor"]["check"]["arguments"])["host"]
    r = requests.get(host)
    req["monitor"]["result"]= {}
    req["monitor"]["result"]["status"] = "ok" if r.status_code == 200 else "fail"
    req["monitor"]["result"]["check"] = req["monitor"]["check"]
    del req["monitor"]["check"]
    print req
    print r.status_code
    resp = json.dumps(req)
    channel.basic_publish(exchange='results',
                          routing_key='',
                          body=resp)

channel.basic_consume(callback,
                      queue='http',
                      no_ack=True)
channel.start_consuming()
