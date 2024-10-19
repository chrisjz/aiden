using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;
using TMPro;

namespace AIden
{
    public class BrainController : MonoBehaviour
    {
        [Header("Agent Profile")]
        [Tooltip("Unique ID of agent.")]
        public string agentId = "1";
        [Tooltip("Name of agent.")]
        public string agentName = "AIden";

        [Header("Configuration")]
        [Tooltip("File path to brain configuration.")]
        public string configPath = "./config/brain/default.json";
        [Header("Output")]
        [Tooltip("Log output to display AI output.")]
        public TMP_Text logOutput;

        [Header("Toggle Sensors")]
        [Tooltip("Toggle auditory ambient sensor.")]
        public bool toggleAuditoryAmbient = true;
        [Tooltip("Toggle tactile sensor.")]
        public bool toggleTactileAction = true;
        [Tooltip("Toggle vision sensor.")]
        public bool toggleVision = true;

        [Header("Actions")]
        [Tooltip("Movement distance per action, in unity units (approximately 1 meter).")]
        public float moveDistance = 1.0f;

        [Header("Cycle Settings")]
        [Tooltip("Frequency in seconds of feeding external sensory to brain for responses. Set to 0 to disable.")]
        public float cycleTime = 1.0f;

        [Header("Simulation Settings")]
        [Tooltip("Enable simulated inputs/responses instead of using real APIs.")]
        public bool enableSimulationMode = false;
        [Tooltip("Sequential list of sensory inputs and outputs for AI to perform.")]
        public List<Sensory> simulatedSensoryInputs = new List<Sensory>();  // User-defined sensory inputs

        private int _simulationIndex = 0;  // To track the current index in the simulation list

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
            _actionManager.SetMoveDistance(moveDistance);

            // Initialize API clients if not in simulation mode
            if (!enableSimulationMode)
            {
                AIAudioCapture audioCapture = GetComponentInChildren<AIAudioCapture>();
                Camera cameraCapture = GetComponentInChildren<Camera>();

                _auditoryApiClient = new AuditoryAPIClient(audioCapture);
                _visionApiClient = new VisionAPIClient(cameraCapture);

                _isAuditoryAmbientSensorEnabled = toggleAuditoryAmbient && _auditoryApiClient.IsAPIEnabled();
                _isVisionSensorEnabled = toggleVision && _visionApiClient.IsAPIEnabled();
                _isTactileActionSensorEnabled = toggleTactileAction;

                if (!_isAuditoryAmbientSensorEnabled && !_isTactileActionSensorEnabled && !_isVisionSensorEnabled)
                {
                    Debug.LogError("No sensor APIs are enabled. At least one sensor is required for cortical processing.");
                    if (logOutput != null) logOutput.text += $"<color=#FF9999>No sensor APIs are enabled. At least one sensor is required for cortical processing.</color>\n";
                    return;
                }

                // Set the Cortical API URL
                if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
                    env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
                    env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
                {
                    _corticalApiUrl = $"{protocol}://{host}:{port}/cortical/";
                    Debug.Log($"Cortical API URL set to: {_corticalApiUrl}");
                    if (logOutput != null) logOutput.text += $"<color=#C0C0C0>Cortical API URL set to: {_corticalApiUrl}</color>\n";
                }
                else
                {
                    Debug.LogError("Missing environment variables for cortical API URL.");
                    if (logOutput != null) logOutput.text += $"<color=#FF9999>Missing environment variables for cortical API URL.</color>\n";
                    return;
                }
            }

            // Start the sensory data processing loop
            StartCoroutine(ProcessSensoryDataLoop());
        }

        private IEnumerator ProcessSensoryDataLoop()
        {
            while (cycleTime > 0.0f)
            {
                if (enableSimulationMode)
                {
                    // Process fake/simulated sensory data
                    yield return StartCoroutine(ProcessSimulatedSensoryData());
                }
                else
                {
                    // Process real sensory data
                    yield return StartCoroutine(ProcessSensoryData());
                }

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
                if (logOutput != null) logOutput.text += $"<color=#FF9999>No sensory data available for cortical processing.</color>\n";
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
                if (logOutput != null) logOutput.text += $"<color=#FF9999>Cortical API call failed: {corticalRequest.error}</color>\n";
                yield break;
            }

            // Process Cortical Response
            string corticalResponseJson = corticalRequest.downloadHandler.text;
            Debug.Log("Cortical Response: " + corticalResponseJson);

            // Deserialize the response
            CorticalResponse corticalResponse = JsonUtility.FromJson<CorticalResponse>(corticalResponseJson);

            // Output to text object if set
            if (logOutput != null)
            {
                string agentDisplayName = $"<b><color=#6666FF>{agentName}</color></b>";  // Bold and blue
                string output = $"{agentDisplayName}\n";

                if (!string.IsNullOrEmpty(corticalResponse.speech))
                {
                    output += $"<b>Speech</b>: {corticalResponse.speech}\n";
                }

                if (!string.IsNullOrEmpty(corticalResponse.thoughts))
                {
                    output += $"<b>Thoughts</b>: {corticalResponse.thoughts}\n";
                }

                if (!string.IsNullOrEmpty(corticalResponse.action))
                {
                    output += $"<b>Action</b>: {corticalResponse.action}\n";
                }

                // Set the output text
                logOutput.text += output;
            }

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
                    if (logOutput != null) logOutput.text += $"<color=#FF9999>Unrecognized action: {corticalResponse.action}</color>\n";
                }
            }
        }

        private IEnumerator ProcessSimulatedSensoryData()
        {
            // If no simulation inputs are defined, use a default sensory input
            if (simulatedSensoryInputs.Count == 0)
            {
                simulatedSensoryInputs.Add(new Sensory
                {
                    vision = new List<VisionInput> { new VisionInput(VisionType.GENERAL, "A room.") },
                    auditory = new List<AuditoryInput> { new AuditoryInput(AuditoryType.AMBIENT, "Birds chirping.") },
                    tactile = new List<TactileInput> { new TactileInput(TactileType.ACTION, null, new AIAction("moveforward")) }
                });
            }

            // Cycle through the simulation list
            var simulatedInput = simulatedSensoryInputs[_simulationIndex];
            _simulationIndex = (_simulationIndex + 1) % simulatedSensoryInputs.Count;  // Loop through the list

            // Simulate cortical response by echoing the sensory inputs
            string action = null;
            string speech = null;
            string thoughts = $"I see... {string.Join(", ", simulatedInput.vision.Select(v => v.content))}, " +
                  $"I hear... {string.Join(", ", simulatedInput.auditory.Select(a => a.content))}";

            // Execute action based on the tactile input (if any)
            foreach (var tactileInput in simulatedInput.tactile)
            {
                if (tactileInput.type == "action" && tactileInput.command != null)
                {
                    AIActionManager.ActionType outputActionType;
                    if (Enum.TryParse(tactileInput.command.name, true, out outputActionType))  // Case-insensitive comparison
                    {
                        _actionManager.ExecuteAction(outputActionType);
                        action = outputActionType.ToString();
                        break;  // Only one action is supported for now.
                    }
                }
            }

            CorticalResponse response = new CorticalResponse
            {
                action = action,
                speech = speech,
                thoughts = thoughts
            };

            // Output simulated cortical response
            Debug.Log("Simulated Cortical Response: " + response);

            // Output to text object if set
            if (logOutput != null)
            {
                string agentDisplayName = $"<b><color=#6666FF>{agentName}</color></b>";  // Bold and blue
                string output = $"{agentDisplayName}\n";

                if (!string.IsNullOrEmpty(response.speech))
                {
                    output += $"<b>Speech</b>: {response.speech}\n";
                }

                if (!string.IsNullOrEmpty(response.thoughts))
                {
                    output += $"<b>Thoughts</b>: {response.thoughts}\n";
                }

                if (!string.IsNullOrEmpty(response.action))
                {
                    output += $"<b>Action</b>: {response.action}\n";
                }

                // Set the output text
                logOutput.text += output;
            }

            yield return null;
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

    public override string ToString()
    {
        return $"Action: {action ?? "None"}, Thoughts: {thoughts ?? "None"}, Speech: {speech ?? "None"}";
    }
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
