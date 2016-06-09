#!/usr/bin/env python
import pika
import json
import requests

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()
channel.queue_declare(queue='http')

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
    print resp
    channel.queue_declare(queue='results')
    channel.basic_publish(exchange='',
                          routing_key='results',
                          body=resp)

channel.basic_consume(callback,
                      queue='http',
                      no_ack=True)
channel.start_consuming()
