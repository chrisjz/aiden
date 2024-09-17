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


        [Header("Toggle Sensors")]
        [Tooltip("Toggle sensory inputs")]
        public bool toggleAuditoryAmbient = true;
        public bool toggleTactileAction = true;
        public bool toggleVision = true;

        [Header("Cycle Settings")]
        [Tooltip("Frequency in seconds of feeding external sensory to brain for responses. Set to 0 to disable.")]
        public float cycleTime = 1.0f;

        private AuditoryAPIClient _auditoryApiClient;
        private VisionAPIClient _visionApiClient;
        private string _corticalApiUrl;

        private AIActionManager _actionManager;

        private bool _isAuditoryAmbientSensorEnabled = false;
        private bool _isTactileActionSensorEnabled = false;
        private bool _isVisionSensorEnabled = false;

        private void Start()
        {
            // Initialize the action manager
            _actionManager = GetComponentInChildren<AIActionManager>();

            // Find the AI audio capture (ear sensor) in child GameObjects
            AIAudioCapture audioCapture = GetComponentInChildren<AIAudioCapture>();

            // Find the camera (eye sensor) in child GameObjects
            Camera cameraCapture = GetComponentInChildren<Camera>();

            // Initialize API clients
            _auditoryApiClient = new AuditoryAPIClient(audioCapture);
            _visionApiClient = new VisionAPIClient(cameraCapture);

            // Check if sensors and related APIs are enabled
            _isAuditoryAmbientSensorEnabled = toggleAuditoryAmbient && _auditoryApiClient.IsAPIEnabled();
            _isVisionSensorEnabled = toggleVision && _visionApiClient.IsAPIEnabled();
            _isTactileActionSensorEnabled = toggleTactileAction;

            if (!_isAuditoryAmbientSensorEnabled && !_isTactileActionSensorEnabled && !_isVisionSensorEnabled)
            {
                Debug.LogError("No sensor APIs are enabled. At least one sensor is required for cortical processing.");
                return;
            }

            // Set the Cortical API URL
            if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
                env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
                env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
            {
                _corticalApiUrl = $"{protocol}://{host}:{port}/cortical/";
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

            // Fetch Occipital Data (Vision) if enabled
            if (_isVisionSensorEnabled)
            {
                yield return StartCoroutine(_visionApiClient.GetVisionDataCoroutine(
                    occipitalData => sensoryInput.vision.Add(new VisionInput(VisionType.GENERAL, occipitalData)),
                    error => Debug.LogError(error)
                ));
            }

            // Fetch Auditory Data (Ambient Noise) if enabled
            if (_isAuditoryAmbientSensorEnabled)
            {
                yield return StartCoroutine(_auditoryApiClient.GetAuditoryDataCoroutine(
                    auditoryData => sensoryInput.auditory.Add(new AuditoryInput(AuditoryType.AMBIENT, auditoryData)),
                    error => Debug.LogError(error)
                ));
            }

            // Fetch Tactile Data (Actions) if enabled
            if (_isTactileActionSensorEnabled)
            {
                foreach (var actionEntry in _actionManager.ActionMap)
                {
                    var inputActionType = actionEntry.Key;
                    var inputAction = actionEntry.Value;

                    AIAction actionCommand = new AIAction(inputActionType.ToString().ToLower(), inputAction.description);
                    sensoryInput.tactile.Add(new TactileInput(TactileType.ACTION, command: actionCommand));
                }
            }

            // Ensure at least one sensory input is available
            if (sensoryInput.vision.Count == 0 && sensoryInput.auditory.Count == 0 && sensoryInput.auditory.Count == 0)
            {
                Debug.LogError("No sensory data available for cortical processing.");
                yield break;
            }

            // Send to Cortical API
            CorticalRequest corticalRequestData = new CorticalRequest
            {
                agent_id = agentId,
                config = configPath,
                sensory = sensoryInput
            };

            string corticalRequestJson = JsonUtility.ToJson(corticalRequestData);
            Debug.Log("Cortical request JSON: " + corticalRequestJson);
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

            // Process Cortical Response
            string corticalResponseJson = corticalRequest.downloadHandler.text;
            Debug.Log("Cortical Response: " + corticalResponseJson);

            // Deserialize the response
            CorticalResponse corticalResponse = JsonUtility.FromJson<CorticalResponse>(corticalResponseJson);

            // Check if action is null
            if (string.IsNullOrEmpty(corticalResponse.action))
            {
                // Do nothing if the action is null or empty
                Debug.Log("No action returned from cortical response.");
            }
            else
            {
                // Map the action from the response
                AIActionManager.ActionType outputActionType;
                if (Enum.TryParse(corticalResponse.action, true, out outputActionType))  // Case-insensitive comparison
                {
                    _actionManager.ExecuteAction(outputActionType);
                }
                else
                {
                    Debug.LogError($"Unrecognized action: {corticalResponse.action}");
                }
            }
        }
    }
}


[Serializable]
public class Sensory
{
    public List<VisionInput> vision = new List<VisionInput>();
    public List<AuditoryInput> auditory = new List<AuditoryInput>();
    public List<TactileInput> tactile = new List<TactileInput>();
    public List<OlfactoryInput> olfactory = new List<OlfactoryInput>();
    public List<GustatoryInput> gustatory = new List<GustatoryInput>();
}

[Serializable]
public class AIAction
{
    public string name;
    public string description;  // Optional

    public AIAction(string name, string description = null)
    {
        this.name = name;
        this.description = description;
    }
}

[Serializable]
public class VisionInput
{
    public string type;
    public string content;

    public VisionInput(VisionType visionType, string content)
    {
        this.type = visionType.ToString().ToLower();
        this.content = content;
    }
}

[Serializable]
public class AuditoryInput
{
    public string type;
    public string content;

    public AuditoryInput(AuditoryType auditoryType, string content)
    {
        this.type = auditoryType.ToString().ToLower();
        this.content = content;
    }
}

[Serializable]
public class TactileInput
{
    public string type;
    public string content;  // Optional, required if type is GENERAL
    public AIAction command;  // Optional, required if type is ACTION

    public TactileInput(TactileType tactileType, string content = null, AIAction command = null)
    {
        this.type = tactileType.ToString().ToLower();

        if (tactileType == TactileType.GENERAL)
        {
            if (string.IsNullOrEmpty(content))
            {
                throw new ArgumentException("`content` is required for GENERAL tactile type.");
            }
            this.content = content;
        }
        else if (tactileType == TactileType.ACTION)
        {
            if (command == null)
            {
                throw new ArgumentException("`command` is required for ACTION tactile type.");
            }
            this.command = command;
        }
    }
}


[Serializable]
public class OlfactoryInput
{
    public OlfactoryType type = OlfactoryType.GENERAL;
    public string content;
}

[Serializable]
public class GustatoryInput
{
    public GustatoryType type = GustatoryType.GENERAL;
    public string content;
}

[Serializable]
public class CorticalRequest
{
    public string agent_id;
    public string config;
    public Sensory sensory;
}

[Serializable]
public class CorticalResponse
{
    public string action;
    public string thoughts;
    public string speech;
}

// Enums for sensory types
public enum VisionType
{
    GENERAL
}

public enum AuditoryType
{
    LANGUAGE,
    AMBIENT
}

[Serializable]
public enum TactileType
{
    GENERAL,
    ACTION
}

[Serializable]
public enum OlfactoryType
{
    GENERAL
}

[Serializable]
public enum GustatoryType
{
    GENERAL
}
