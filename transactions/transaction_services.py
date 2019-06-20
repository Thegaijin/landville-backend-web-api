"""A module that provides services associated financial transactions"""
import os
import hashlib
import requests
import json
import datetime
import base64
from Cryptodome.Cipher import DES3
from urllib.parse import urljoin


class TransactionServices:

    rave_public_key = os.getenv('RAVE_TEST_PUBLIC_KEY')
    rave_secret_key = os.getenv('RAVE_TEST_SECRET_KEY')
    redirect_url = os.getenv('RAVE_REDIRECT_URL')

    @classmethod
    def get_key(cls):
        """
        A function that uses the secret key to generate encryption key
        :return: encryption key
        """

        hashed_secret_key = hashlib.md5(
            cls.rave_secret_key.encode("utf-8")
        ).hexdigest()
        hashed_secret_key_last12 = hashed_secret_key[-12:]
        secret_key_adjusted = cls.rave_secret_key.replace('FLWSECK-', '')
        secret_key_adjusted_first12 = secret_key_adjusted[:12]
        return secret_key_adjusted_first12 + hashed_secret_key_last12

    @staticmethod
    def encrypt_data(key, plain_text):
        """
        This is the encryption function that encrypts your payload by
        passing the text and your encryption Key.
        :param key: str: DES3 encryption key
        :param plain_text: Dict: the payload to be encrypted before calling
        rave endpoint
        :return: Encrypted payload to send to rave endpoint
        """

        block_size = 8
        pad_diff = block_size - (len(plain_text) % block_size)
        cipher = DES3.new(key, DES3.MODE_ECB)
        plain_text = f'{plain_text}{"".join(chr(pad_diff) * pad_diff)}'
        test = plain_text.encode('utf-8')
        encrypted = base64.b64encode(cipher.encrypt(test)).decode('utf-8')
        return encrypted

    @classmethod
    def rave_call(cls, data):
        """
        A method that sends encrypted payment data to rave platform
        :param data: data encrypted with DES3
        :return: JSON response from rave endpoint
        """
        hashed_sec_key = cls.get_key()
        encrypt_3DES_key = cls.encrypt_data(hashed_sec_key, json.dumps(data))

        payload = {
            'PBFPubKey': cls.rave_public_key,
            'client': encrypt_3DES_key,
            'alg': '3DES-24'
        }

        endpoint = urljoin(os.getenv('RAVE_URL'),
                           'flwv3-pug/getpaidx/api/charge')
        headers = {'content-type': 'application/json'}
        response = requests.post(
            endpoint, headers=headers, data=json.dumps(payload))
        return response.json()

    @classmethod
    def initiate_card_payment(cls, pay_data):
        """
        A method that initiate card payment
        :param pay_data: dict: information about the card and user making
        payment. Rave uses this to determine if the payment is local or foreign
        :return: JSON response from rave endpoint
        """
        data = {
            'PBFPubKey': cls.rave_public_key,
            'cardno': pay_data.get('cardno'),
            'cvv': pay_data.get('cvv'),
            'expirymonth': pay_data.get('expirymonth'),
            'expiryyear': pay_data.get('expiryyear'),
            'currency': 'NGN',
            'country': pay_data.get('country', 'NG'),
            'amount': pay_data.get('amount'),
            'email': pay_data.get('email'),
            'firstname': pay_data.get('email'),
            'lastname': pay_data.get('email'),
            'txRef': f'LANDVILLE-{datetime.datetime.now()}',
            'redirect_url': cls.redirect_url
        }

        return cls.rave_call(data)

    @classmethod
    def authenticate_card_payment(cls, pay_data):
        """
        A method that provide the needed authentication for payment.
        Payment with Nigerian local card is authenticated with card pin.
        Payment with international card is authenticated with the customer's
        billing address details . Customers can easily find these on their
        bank statements.
        :param pay_data: payment data
        :return: JSON response
        """

        data = {
            'PBFPubKey': cls.rave_public_key,
            'cardno': pay_data.get('cardno'),
            'cvv': pay_data.get('cvv'),
            'expirymonth': pay_data.get('expirymonth'),
            'expiryyear': pay_data.get('expiryyear'),
            'currency': 'NGN',
            'country': pay_data.get('country', 'NG'),
            'amount': pay_data.get('amount'),
            'email': pay_data.get('email'),
            'firstname': pay_data.get('firstname'),
            'lastname': pay_data.get('lastname'),
            'txRef': f'LANDVILLE-{datetime.datetime.now()}',
            'redirect_url': TransactionServices.redirect_url
        }

        data.update(pay_data['auth_dict'])

        return cls.rave_call(data)

    @classmethod
    def validate_card_payment(cls, flwref, otp):
        """
        A method that validates card payment.
        For Nigerian credit/debit cards, validation is done via OTP
        :param flwref: flutterwave
        :param otp: OTP send to the user to validate transaction
        :return: JSON response
        """
        data = {
            'PBFPubKey': cls.rave_public_key,
            'transaction_reference': flwref,
            'otp': otp
        }

        endpoint = urljoin(os.getenv('RAVE_URL'),
                           'flwv3-pug/getpaidx/api/validatecharge')
        headers = {'content-type': 'application/json'}
        response = requests.post(
            endpoint, headers=headers, data=json.dumps(data))
        response_json = response.json()
        response_json['status_code'] = response.status_code
        return response_json