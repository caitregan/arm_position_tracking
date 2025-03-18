#testing

from television import VRInteraction
from VRDataCollection import VRDataOutput

if __name__ == 'main':
    VR_Interact = VRInteraction(cert_file="../cert.pem", key_file="../key.pem")

    while True:
        head_matrix = VRDataOutput.get_data()[0]
        print("Head Matrix:", head_matrix)