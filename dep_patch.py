import json
import os
import getpass
from datetime import datetime
from base64 import b64encode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm

def sign_message(priv, message):
    return priv.sign(message, ec.ECDSA(hashes.SHA256()))

def verify_signature(pub, message, signature):
    try:
        pub.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False

def build_doctor_record() -> str:
    name = input('Patient name: ').strip()
    avs = input('Patient AVS number: ').strip()
    drugs = {}
    print("Enter drugs and dosages. Leave drug name empty to finish.")
    while True:
        drug = input('Drug name: ').strip()
        if not drug:
            break
        dosage = input('Dosage (string): ').strip()
        drugs[drug] = dosage

    record_data = {
        "timestamp": datetime.now().isoformat(),
        "patient_name": name,
        "patient_avs": avs,
        "drugs": drugs
    }

    return json.dumps(record_data).encode("utf-8")


def build_patient_record() -> str:
    name = input('Patient name: ').strip()
    avs = input('Patient AVS number: ').strip()
    symptoms = {}
    print("Enter symptoms and their temporality. Leave symptom name empty to finish.")
    while True:
        sym = input('Symptom: ').strip()
        if not sym:
            break
        temp = input('Temporality (string): ').strip()
        symptoms[sym] = temp

    record_data = {
        "timestamp": datetime.now().isoformat(),
        "patient_name": name,
        "patient_avs": avs,
        "symptoms": symptoms
    }

    return json.dumps(record_data).encode("utf-8")

def save_record_to_db(record, signature, isPatient):
    entry = {
        "record": record.decode(),
        "signature": b64encode(signature).decode('utf-8'),
    }
    filename = "medical_records.txt" if isPatient else "prescriptions_records.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_or_generate_keys():
    priv_file = "ecdsa_private.pem"
    pub_file = "ecdsa_public.pem"
    
    priv = None
    pub = None

    if os.path.exists(priv_file) and os.path.exists(pub_file):
        # Load public key
        with open(pub_file, "rb") as f:
            pub = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        
        # Load private key
        password = getpass.getpass(
            "Enter password to decrypt private key: "
        ).encode('utf-8')

        try:
            with open(priv_file, "rb") as f:
                priv = serialization.load_pem_private_key(
                    f.read(),
                    password=password,
                    backend=default_backend()
                )
            print("Private key decrypted and loaded.")
        except (ValueError, TypeError, UnsupportedAlgorithm):
            print("Incorrect password.")
            return None, None
        
        print("Private key decrypted and loaded.")  
    else:
        print("No keypair found — generating new one...")
        
        # Get a strong password to encrypt the new key
        password = getpass.getpass(
            "Create a strong password to encrypt the new private key: "
        ).encode('utf-8')
        password_confirm = getpass.getpass("Confirm password: ").encode('utf-8')
        
        if password != password_confirm:
            print("Passwords do not match. Aborting.")
            return None, None

        # Generate the keys
        priv = ec.generate_private_key(
            ec.SECP256R1(), default_backend()
        )
        pub = priv.public_key()
        print("New keypair generated.")

        # Serialize and save the private key
        pem_private = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        with open(priv_file, "wb") as f:
            f.write(pem_private)

        # 4. Serialize and save the public key
        pem_public = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(pub_file, "wb") as f:
            f.write(pem_public)
        
        print("New keypair generated and saved.")

    return priv, pub

def main():
    print("Welcome to the medical prescription app. As a patient, you can input your symptoms so that a doctor can verify them and give you a prescription. \n As doctor, you can create prescriptions for a patient. All the records are signed with the platform's private key so that doctors know they read authentic symptoms and pharmacies know they read valid prescriptions. \n")
    # Load or generate keypair. We assume that the public key is safely transfered when needed (ex: for doctors to read the records or for pharamcies to validate prescriptions)
    priv, pub = load_or_generate_keys()
    print('\n\nWho are you? (this replaces a correct login with credentials)')
    print('1) Doctor')#We suppose that in practice, there is a correct login with credentials
    print('2) Patient')
    choice = input('Choose 1 or 2: ').strip()
    record = b""
    isPatient = True
    if choice == '1':
        record = build_doctor_record()
        isPatient = False
    elif choice == '2':
        record = build_patient_record()
        isPatient = True
    else:
        print('Invalid choice')
        return
    signature = sign_message(priv, record)
    save_record_to_db(record, signature, isPatient)
    print('Record signed by system and saved in DB')
    return

if __name__ == '__main__':
    main()
