
#Imports
import Vuer 
from vuer.schemas import Hands, ImageBackground
from pyngrok import ngrok
import numpy as np
from multiprocessing import Array, shared_memory, Process
import time
import asyncio

class JointTracking:
    '''
    The purpose of this class is to track the position of both hands and the neck 
    (i.e. the camera movement) in VR. 
    
    '''
    def __init__(self, cert_file, key_file):
        #Initialize positions to be locked
        self.left_hand_pos = Array('d', 16, lock=True)
        self.right_hand_pos = Array('d', 16, lock=True)
        self.head_pos = Array('d', 16, lock=True)

        self.left_landmarks_pos = Array('d', 16, lock=True)
        self.right_landmarks_pos = Array('d', 16, lock=True)

        #Image Parameters (Oculus)
        self.img_shape = JointTracking.image_specs[0]  #change?

        #Enable usage from remote area or local
        if ngrok:
            self.vuer = Vuer(host='0.0.0.0', queries=dict(grid=False), queue_len=3)
        else:
            self.vuer = Vuer(host='0.0.0.0', cert=cert_file, key=key_file, queries=dict(grid=False), queue_len=3)

        #Event Handlers, updates shared memory constantly
        self.vuer.add_handler("HAND_MOVE")(self.hands_motion)
        self.vuer.add_handler("CAMERA_MOVE")(self.head_motion)

        #shared memory
        existing_shm = shared_memory.SharedMemory(name=JointTracking.image_specs[2])
        #always use binocular vision
        self.vuer.spawn(start=False)(self.main_image)

        #Run process
        self.Process = Process(target=self.run)
        self.process.daemon = True
        self.process.start()

    #Start Process
    def run(self):
        self.vuer.run()

    #create a shared memory & other image specs
    def image_specs():
        img_shape = (480, 640*2, 3)
        shm = shared_memory.SharedMemory(create=True, size=np.prod(JointTracking.img_shape)*np.uint8().itemsize)
        shm_name = shm.name
        img_array = np.ndarray(img_shape, dtype=np.uint8, buffer=shm.buf)

        return np.array([img_shape, shm, shm_name, img_array])

    #VR Image
    async def main_image(self, session, fps=60):
        session.upsert(
            Hands(
                fps=fps,
                stream=True,
                key='hands'
            ),
            to='bgChildren',
        )
        while True:
            session.upsert(
                [
                    ImageBackground(  #look into what to write for these specs
                        aspect = 1.667,
                        height=1,
                        distanceToCamera=1,
                        format="jpeg",
                        quality=50,
                        key="background-left",
                        interpolate=True,
                    ),
                    ImageBackground(
                        aspect = 1.667,
                        height=1,
                        distanceToCamera=1,
                        format="jpeg",
                        quality=50,
                        key="background-right",
                        interpolate=True,
                    ),
                ],
                to="bgChildren",
            )
            await asyncio.sleep(0.016*2)

    #Gathers hand positions asynchronously
    async def hands_motion(self,event):
        try:
            self.left_hand_pos[:] = event.value["leftHand"]
            self.right_hand_pos[:] = event.value["rightHand"]
            self.left_landmarks_pos[:] = np.array(event.value["leftLandmarks"]).flatten()
            self.right_landmarks_pos[:] = np.array(event.value["rightLandmarks"]).flatten()
        except:
            pass
    
    #Gathers head/camera position asynchronously
    async def head_motion(self,event):
        try:
            self.head_pos[:] = event.value["camera"]["matrix"]
        except:
            pass

    #Functions for accessibility
    def left_hand(self):
        return np.array(self.left_hand_pos[:]).reshape(4, 4, order="F") #why order F?
    
    def right_hand(self):
        return np.array(self.right_hand_pos[:]).reshape(4, 4, order="F") 
    
    def head(self):
        return np.array(self.head_pos[:]).reshape(4, 4, order="F")
    
    def left_landmarks(self):
        return np.array(self.left_landmarks_pos[:]).reshape(25, 3) #why this size
    
    def right_landmarks(self):
        return np.array(self.right_landmarks_pos[:]).reshape(25, 3) 

if __name__ == '__main__':

    VR_Interact = JointTracking(cert_file="../cert.pem", key_file="../key.pem") #what else do we need here
    #Run constantly 
    while True:
        time.sleep(0.05) #how fast we want to gather hand joint data
