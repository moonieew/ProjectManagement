from flask import Flask, render_template, jsonify, request, flash
import paypalrestsdk

app = Flask(__name__)

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AdpFE5uzDjkw12pjMNkYIUxvlr1sVYntW2o5jrqxABbHxW-7tcUvl7Otd0KVOEsL_RV8sfDgQlqPn1_z",
  "client_secret": "EJ3XBSzYJH7Zs28pQGkHv_PlqJhxC2xZ_c2hbGgAk09vPV0m7luYrbz7nMCnDIVawKY3I5tADjeb5kAG" })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payment', methods=['POST'])
def payment():

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Payment Fee",
                    "sku": "12345",
                    "price": "500.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "1.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

@app.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        flash('Execute success!')
        success = True
    else:
        print(payment.error)


    return jsonify({'success' : success})



DEFAULT_PORT = 5433
if __name__ == "__main__":
    app.run(debug=True, port=DEFAULT_PORT)


