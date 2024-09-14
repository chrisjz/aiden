using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;

namespace AIden
{
    public class BrainController : MonoBehaviour
    {
        [Header("Agent Profile")]
        [Tooltip("Unique ID of agent")]
        public string agentId = "1";
        [Tooltip("Name of agent")]
        public string agentName = "AIden";

        [Header("Configuration")]
        [Tooltip("File path to brain configuration")]
        public string configPath = "./config/brain/default.json";
        public PlayerInputs aiInputs;

        [Header("Cycle Settings")]
        [Tooltip("Frequency in seconds of feeding external sensory to brain for responses. Set to 0 to disable.")]
        public float cycleTime = 1.0f;

        private AuditoryAPIClient _auditoryApiClient;
        private VisionAPIClient _visionApiClient;
        private string _corticalApiUrl;

        private bool _isAuditoryApiEnabled = false;
        private bool _isVisionApiEnabled = false;

        private void Start()
        {
            // Find the AI audio capture (ear sensor) in child GameObjects
            AIAudioCapture audioCapture = GetComponentInChildren<AIAudioCapture>();

            // Find the camera (eye sensor) in child GameObjects
            Camera cameraCapture = GetComponentInChildren<Camera>();

            // Initialize API clients
            _auditoryApiClient = new AuditoryAPIClient(audioCapture);
            _visionApiClient = new VisionAPIClient(cameraCapture);

            // Check if APIs are enabled
            _isAuditoryApiEnabled = _auditoryApiClient.IsAPIEnabled();
            _isVisionApiEnabled = _visionApiClient.IsAPIEnabled();

            if (!_isAuditoryApiEnabled && !_isVisionApiEnabled)
            {
                Debug.LogError("No sensor APIs are enabled. At least one sensor is required for cortical processing.");
                return;
            }

            // Set the Cortical API URL
            if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
                env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
                env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
            {
                _corticalApiUrl = $"{protocol}://{host}:{port}/cortical";
                Debug.Log($"Cortical API URL set to: {_corticalApiUrl}");
            }
            else
            {
                Debug.LogError("Missing environment variables for cortical API URL.");
                return;
            }

            // Start the sensory data processing loop
            StartCoroutine(ProcessSensoryDataLoop());
        }

        // private void Update()
        // {
        //     // Example: Make AI move forward continuously
        //     Vector2 moveDirection = new Vector2(0, 1);  // Move forward
        //     aiInputs.MoveInput(moveDirection);
        // }

        private IEnumerator ProcessSensoryDataLoop()
        {
            while (cycleTime > 0.0f)
            {
                // Process sensory data asynchronously
                yield return StartCoroutine(ProcessSensoryData());

                // Wait for the defined cycle time before starting the next cycle
                yield return new WaitForSeconds(cycleTime);
            }
        }

        private IEnumerator ProcessSensoryData()
        {
            Sensory sensoryInput = new Sensory();

            // Step 1: Fetch Occipital Data (Vision) if enabled
            if (_isVisionApiEnabled)
            {
                yield return StartCoroutine(_visionApiClient.GetVisionDataCoroutine(
                    occipitalData => sensoryInput.vision.Add(new VisionInput { type = "general", content = occipitalData }),
                    error => Debug.LogError(error)
                ));
            }

            // Step 2: Fetch Auditory Data (Ambient Noise) if enabled
            if (_isAuditoryApiEnabled)
            {
                yield return StartCoroutine(_auditoryApiClient.GetAuditoryDataCoroutine(
                    auditoryData => sensoryInput.auditory.Add(new AuditoryInput { type = "ambient", content = auditoryData }),
                    error => Debug.LogError(error)
                ));
            }

            // Ensure at least one sensory input is available
            if (sensoryInput.vision.Count == 0 && sensoryInput.auditory.Count == 0)
            {
                Debug.LogError("No sensory data available for cortical processing.");
                yield break;
            }

            // Step 3: Send to Cortical API
            CorticalRequest corticalRequestData = new CorticalRequest
            {
                agent_id = agentId,
                config = configPath,
                sensory = sensoryInput
            };

            string corticalRequestJson = JsonUtility.ToJson(corticalRequestData);
            UnityWebRequest corticalRequest = new UnityWebRequest(_corticalApiUrl, "POST")
            {
                uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(corticalRequestJson)),
                downloadHandler = new DownloadHandlerBuffer()
            };
            corticalRequest.SetRequestHeader("Content-Type", "application/json");

            yield return corticalRequest.SendWebRequest();
            if (corticalRequest.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Cortical API call failed: " + corticalRequest.error);
                yield break;
            }

            // Step 4: Process Cortical Response
            string corticalResponse = corticalRequest.downloadHandler.text;
            Debug.Log("Cortical Response: " + corticalResponse);
        }
    }
}


[Serializable]
public class Sensory
{
    public List<VisionInput> vision = new List<VisionInput>();
    public List<AuditoryInput> auditory = new List<AuditoryInput>();
}

[Serializable]
public class VisionInput
{
    public string type;
    public string content;
}

[Serializable]
public class AuditoryInput
{
    public string type;
    public string content;
}

[Serializable]
public class CorticalRequest
{
    public string agent_id;
    public string config;
    public Sensory sensory;
}