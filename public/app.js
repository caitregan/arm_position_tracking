let ws;
let xrSession = null;

async function connectWebSocket() {
  ws = new WebSocket('ws://10.0.0.158:8012'); // Change this to your laptop's IP + port

  ws.onopen = () => console.log('WebSocket connected');
  ws.onclose = () => console.log('WebSocket closed');
  ws.onerror = (error) => console.error('WebSocket error:', error);
}

async function initXR() {
  if (!navigator.xr) {
    console.error('WebXR not supported');
    return;
  }

  const supported = await navigator.xr.isSessionSupported('immersive-vr');
  if (!supported) {
    console.error('Immersive VR not supported');
    return;
  }

  xrSession = await navigator.xr.requestSession('immersive-vr', {
    optionalFeatures: ['hand-tracking']
  });

  const refSpace = await xrSession.requestReferenceSpace('local');

  xrSession.addEventListener('end', () => {
    console.log('XR Session ended');
    xrSession = null;
  });

  const onXRFrame = (time, frame) => {
    const session = frame.session;
    session.requestAnimationFrame(onXRFrame);

    const inputSources = session.inputSources;

    const handsData = {
      leftHand: null,
      rightHand: null,
      leftLandmarks: [],
      rightLandmarks: []
    };

    inputSources.forEach((source) => {
      if (source.hand) {
        const handedness = source.handedness; // 'left' or 'right'
        const landmarks = [];

        for (let jointName of source.hand.keys()) {
          const joint = source.hand.get(jointName);
          if (joint && joint.transform) {
            const pos = joint.transform.position;
            landmarks.push([pos.x, pos.y, pos.z]);
          }
        }

        if (handedness === 'left') {
          handsData.leftHand = source.targetRaySpace?.transform?.matrix || [];
          handsData.leftLandmarks = landmarks;
        } else if (handedness === 'right') {
          handsData.rightHand = source.targetRaySpace?.transform?.matrix || [];
          handsData.rightLandmarks = landmarks;
        }
      }
    });

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'HAND_MOVE',
        value: handsData
      }));
    }
  };

  xrSession.requestAnimationFrame(onXRFrame);
}

document.getElementById('enter-vr').addEventListener('click', async () => {
  await connectWebSocket();
  await initXR();
});
