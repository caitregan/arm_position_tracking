#testing

from television import JointTracking
from VRDataCollection import ChangeOfBasis

import time

if __name__ == '__main__':
    #VR_Interact = JointTracking(cert_file="../cert.pem", key_file="../key.pem")

    while True:
        COB = ChangeOfBasis()

        head_matrix = COB.get_data()[0]
        left_fingers_matrix = COB.get_data()[3]
        right_fingers_matrix = COB.get_data()[4]

        print("Head Matrix:", head_matrix)
        print("Left Fingers:", left_fingers_matrix)
        print("Right Fingers:", right_fingers_matrix)

        time.sleep(0.01)