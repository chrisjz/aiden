using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;
using TMPro;
using System.Threading.Tasks;
using PimDeWitte.UnityMainThreadDispatcher;
using UnityEngine.InputSystem;
using Unity.VisualScripting;

public static class UnityWebRequestExtensions
{
    public static Task<UnityWebRequest> SendWebRequestAsync(this UnityWebRequest request)
    {
        var tcs = new TaskCompletionSource<UnityWebRequest>();

        request.SendWebRequest().completed += operation =>
        {
            if (request.result == UnityWebRequest.Result.Success)
            {
                tcs.SetResult(request);
            }
            else
            {
                tcs.SetException(new UnityWebRequestException(request.error));
            }
        };

        return tcs.Task;
    }
}

public class UnityWebRequestException : System.Exception
{
    public UnityWebRequestException(string message) : base(message) { }
}

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
        [Tooltip("Chat output to display AI output.")]
        public TMP_Text chatOutput;

        [Header("Toggle Sensors")]
        [Tooltip("Toggle auditory ambient sensor.")]
        public bool toggleAuditoryAmbient = true;
        [Tooltip("Toggle auditory language sensor.")]
        public bool toggleAuditoryLanguage = true;
        [Tooltip("Toggle tactile action sensor.")]
        public bool toggleTactileAction = true;
        [Tooltip("Toggle tactile collision sensor.")]
        public bool toggleTactileCollision = true;
        [Tooltip("Toggle vision sensor.")]
        public bool toggleVision = true;

        [Header("Sensory Execution Mode")]
        [Tooltip("Toggle between parallel and sequential execution of sensory tasks. Running in parallel where sensory APIs are on the same machine may cause performance degradation.")]
        public bool runSensoryTasksInParallel = false; // Default is sequential

        [Header("Sensory Inputs")]
        [Tooltip("Buffer for auditory language inputs received from users or other agents.")]
        public List<AuditoryInput> auditoryLanguageBufferList = new List<AuditoryInput>();

        [Header("Actions")]
        [Tooltip("Movement distance per action, in unity units (approximately 1 meter).")]
        public float moveDistance = 1.0f;
        [Tooltip("Toggle passing an action's description to the brain API.")]
        public bool toggleActionDescriptions = true;

        [Header("Resource Settings")]
        [Tooltip("When using the same GPU for Unity and inference servers, enabling this will allow Unity to reduce GPU resource when making inference calls.")]
        public bool toggleGPUThrottling = true;
        [Tooltip("Reduce Unity graphics quality level to this when making inference calls.")]
        public int throttleQualityLevel = 0;
        [Tooltip("Reduce Unity frame rate to this when making inference calls.")]
        public int throttleFrameRate = 30;

        [Header("Cycle Settings")]
        [Tooltip("Freeze the agent. The cycle loop will be disabled.")]
        public bool freeze = false;
        [Tooltip("Frequency in seconds of feeding external sensory to brain for responses.")]
        public float cycleTime = 1.0f;

        [Header("Simulation Settings")]
        [Tooltip("Enable simulated inputs/responses instead of using real APIs.")]
        public bool enableSimulationMode = false;
        [Tooltip("Sequential list of sensory inputs and outputs for AI to perform.")]
        public List<Sensory> simulatedSensoryInputs = new List<Sensory>();

        private int _simulationIndex = 0;  // To track the current index in the simulation list

        private CharacterCollisionDetector _collisionDetector;

        private AuditoryAPIClient _auditoryApiClient;
        private VisionAPIClient _visionApiClient;
        private string _corticalApiUrl;

        private AIActionManager _actionManager;

        private bool _isAuditoryAmbientSensorEnabled = false;
        private bool _isAuditoryLanguageSensorEnabled = false;
        private bool _isTactileActionSensorEnabled = false;
        private bool _isTactileCollisionSensorEnabled = false;
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
                _isAuditoryLanguageSensorEnabled = toggleAuditoryLanguage;
                _isVisionSensorEnabled = toggleVision && _visionApiClient.IsAPIEnabled();
                _isTactileActionSensorEnabled = toggleTactileAction;
                _isTactileCollisionSensorEnabled = toggleTactileCollision;

                if (!_isAuditoryAmbientSensorEnabled && !_isAuditoryLanguageSensorEnabled && !_isTactileActionSensorEnabled && !_isTactileCollisionSensorEnabled && !_isVisionSensorEnabled)
                {
                    Debug.LogError("No sensor APIs are enabled. At least one sensor is required for cortical processing.");
                    if (logOutput != null) logOutput.text += "<color=#FF9999>No sensor APIs are enabled. At least one sensor is required for cortical processing.</color>\n";
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
                    if (logOutput != null) logOutput.text += "<color=#FF9999>Missing environment variables for cortical API URL.</color>\n";
                    return;
                }
            }

            // Initialize collision detector
            _collisionDetector = GetComponentInParent<CharacterCollisionDetector>();

            // Start the sensory data processing loop
            ProcessSensoryDataLoop();
        }

        private async void ProcessSensoryDataLoop()
        {
            while (cycleTime >= 0.0f)
            {
                // Wait for the defined cycle time before starting the next cycle
                await Task.Delay(TimeSpan.FromSeconds(cycleTime));

                if (freeze) continue;

                if (enableSimulationMode)
                {
                    // Process fake/simulated sensory data
                    ProcessSimulatedSensoryData();
                }
                else
                {
                    // Process real sensory data
                    await ProcessSensoryData();
                }
            }
        }

        private async Task ProcessSensoryData()
        {
            Sensory sensoryInput = new Sensory();

            int originalQualityLevel = 5;
            int originalFrameRate = -1;
            if (toggleGPUThrottling)
            {
                // Get and set the original quality level on the main thread
                originalQualityLevel = await Task.Run(() =>
                {
                    var taskCompletionSource = new TaskCompletionSource<int>();
                    UnityMainThreadDispatcher.Instance().Enqueue(() =>
                    {
                        taskCompletionSource.SetResult(QualitySettings.GetQualityLevel());
                    });
                    return taskCompletionSource.Task;
                });

                // Lower render quality
                UnityMainThreadDispatcher.Instance().Enqueue(() =>
                {
                    QualitySettings.SetQualityLevel(throttleQualityLevel);
                });

                // Get and set the original frame rate on the main thread
                originalFrameRate = await Task.Run(() =>
                {
                    var taskCompletionSource = new TaskCompletionSource<int>();
                    UnityMainThreadDispatcher.Instance().Enqueue(() =>
                    {
                        taskCompletionSource.SetResult(Application.targetFrameRate);
                        Application.targetFrameRate = throttleFrameRate; // Lower the target frame rate
                    });
                    return taskCompletionSource.Task;
                });
            }

            // Fetch Vision Data and Auditory Data (Ambient) if enabled
            if (runSensoryTasksInParallel)
            {
                await RunSensoryTasksInParallel(sensoryInput);
            }
            else
            {
                await RunSensoryTasksSequentially(sensoryInput);
            }

            // Fetch Auditory Data (Language) if enabled
            if (_isAuditoryLanguageSensorEnabled && auditoryLanguageBufferList.Count > 0)
            {
                string speech = string.Join("\n", auditoryLanguageBufferList.Select(a => a.content));
                sensoryInput.auditory.Add(new AuditoryInput(AuditoryType.LANGUAGE, speech));
                auditoryLanguageBufferList.Clear();
            }

            // Fetch Tactile Data (Actions) if enabled
            if (_isTactileActionSensorEnabled)
            {
                foreach (var actionEntry in _actionManager.ActionMap)
                {
                    var inputActionType = actionEntry.Key;
                    var inputAction = actionEntry.Value.action;

                    string actionDescription = toggleActionDescriptions ? inputAction.description : null;

                    AIAction actionCommand = new AIAction(inputActionType.ToString().ToLower(), actionDescription);
                    sensoryInput.tactile.Add(new TactileInput(TactileType.ACTION, command: actionCommand));
                }
            }

            // Fetch Tactile Data (Collisions) if enabled
            if (_isTactileCollisionSensorEnabled && _collisionDetector != null)
            {
                var collision = _collisionDetector.lastDetectedCollision;
                if (collision.collidedObject != null)
                {
                    // TODO: Templatise the input or handle on the API side.
                    var tactileCollisionInput = $"Tactile collision detected on the {collision.region} side.";
                    sensoryInput.tactile.Add(new TactileInput(TactileType.GENERAL, tactileCollisionInput));
                    Debug.Log($"Tactile input detected: {collision.region} with object: {collision.collidedObject.name}");

                    // Clear collisions buffer
                    _collisionDetector.ClearDetectedCollisions();
                }
            }

            // Ensure at least one sensory input is available
            if (sensoryInput.vision.Count == 0 && sensoryInput.auditory.Count == 0 && sensoryInput.tactile.Count == 0 && sensoryInput.olfactory.Count == 0 && sensoryInput.gustatory.Count == 0)
            {
                Debug.LogError("No sensory data available for cortical processing.");
                if (logOutput != null) logOutput.text += "<color=#FF9999>No sensory data available for cortical processing.</color>\n";

                ResetGPUThrottling(originalQualityLevel, originalFrameRate);
                return;
            }

            await SendCorticalRequest(sensoryInput, originalQualityLevel, originalFrameRate);
        }

        private async Task RunSensoryTasksInParallel(Sensory sensoryInput)
        {
            List<Task> sensoryTasks = new List<Task>();

            if (_isVisionSensorEnabled)
            {
                sensoryTasks.Add(Task.Run(async () =>
                {
                    string occipitalData = await _visionApiClient.GetVisionDataAsync();
                    if (occipitalData != null)
                    {
                        sensoryInput.vision.Add(new VisionInput(VisionType.GENERAL, occipitalData));
                    }
                }));
            }

            // Fetch Auditory Data (Ambient Noise) if enabled
            if (_isAuditoryAmbientSensorEnabled)
            {
                sensoryTasks.Add(Task.Run(async () =>
                {
                    string auditoryData = await _auditoryApiClient.GetAuditoryDataAsync();
                    if (auditoryData != null)
                    {
                        sensoryInput.auditory.Add(new AuditoryInput(AuditoryType.AMBIENT, auditoryData));
                    }
                }));
            }

            await Task.WhenAll(sensoryTasks);
        }

        private async Task RunSensoryTasksSequentially(Sensory sensoryInput)
        {
            if (_isVisionSensorEnabled)
            {
                string occipitalData = await _visionApiClient.GetVisionDataAsync();
                if (occipitalData != null)
                {
                    sensoryInput.vision.Add(new VisionInput(VisionType.GENERAL, occipitalData));
                }
            }

            if (_isAuditoryAmbientSensorEnabled)
            {
                string auditoryData = await _auditoryApiClient.GetAuditoryDataAsync();
                if (auditoryData != null)
                {
                    sensoryInput.auditory.Add(new AuditoryInput(AuditoryType.AMBIENT, auditoryData));
                }
            }
        }

        private async Task SendCorticalRequest(Sensory sensoryInput, int originalQualityLevel, int originalFrameRate)
        {
            CorticalRequest corticalRequestData = new CorticalRequest
            {
                agent_id = agentId,
                config = configPath,
                sensory = sensoryInput
            };

            string corticalRequestJson = JsonUtility.ToJson(corticalRequestData);

            using (var corticalRequest = new UnityWebRequest(_corticalApiUrl, "POST"))
            {
                corticalRequest.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(corticalRequestJson));
                corticalRequest.downloadHandler = new DownloadHandlerBuffer();
                corticalRequest.SetRequestHeader("Content-Type", "application/json");

                await corticalRequest.SendWebRequestAsync();

                if (corticalRequest.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError("Cortical API call failed: " + corticalRequest.error);
                    if (logOutput != null) logOutput.text += $"<color=#FF9999>Cortical API call failed: {corticalRequest.error}</color>\n";

                    ResetGPUThrottling(originalQualityLevel, originalFrameRate);
                    return;
                }

                ResetGPUThrottling(originalQualityLevel, originalFrameRate);

                // Process Cortical Response
                string corticalResponseJson = corticalRequest.downloadHandler.text;
                Debug.Log("Cortical Response: " + corticalResponseJson);

                // Deserialize the response
                CorticalResponse corticalResponse = JsonUtility.FromJson<CorticalResponse>(corticalResponseJson);

                // Output to text object if set
                string agentDisplayName = $"<b><color=#6666FF>{agentName}</color></b>";
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
                if (chatOutput != null && corticalResponse.speech != null)
                    chatOutput.text += $"{agentDisplayName}\n{corticalResponse.speech}\n";
                if (logOutput != null) logOutput.text += output;

                // Execute action if available
                if (!string.IsNullOrEmpty(corticalResponse.action))
                {
                    try
                    {

                        _actionManager.ExecuteAction(corticalResponse.action.ToLower());
                    }
                    catch (Exception e)
                    {
                        Debug.LogError(e);
                        if (logOutput != null) logOutput.text += $"<color=#FF9999>Could not execute action: {corticalResponse.action}</color>\n";
                    }
                }
            }
        }

        private void ProcessSimulatedSensoryData()
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
            string thoughts = $"I see... {string.Join(", ", simulatedInput.vision.Select(v => v.content))}, " +
                  $"I hear... {string.Join(", ", simulatedInput.auditory.Select(a => a.content))}";

            // Mirror auditory language inputs received in buffer
            string speech = null;
            if (auditoryLanguageBufferList.Count > 0)
            {
                speech = "Someone said: \"";
                foreach (var auditoryInput in auditoryLanguageBufferList)
                {
                    speech += auditoryInput.content + "\n";
                }

                // Trim the trailing newline character
                speech = speech.TrimEnd('\n') + "\"";

                // Clear buffer
                auditoryLanguageBufferList.Clear();
            }

            // Execute action based on the tactile input (if any)
            string action = null;
            foreach (var tactileInput in simulatedInput.tactile)
            {
                if (tactileInput.type == "action" && tactileInput.command != null)
                {
                    action = tactileInput.command.name;
                    try
                    {
                        _actionManager.ExecuteAction(action);
                        break;  // Only one action is supported for now.
                    }
                    catch (Exception e)
                    {
                        Debug.LogError(e);
                        if (logOutput != null) logOutput.text += $"<color=#FF9999>Could not execute action: {action}</color>\n";
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
            string agentDisplayName = $"<b><color=#6666FF>{agentName}</color></b>";  // Bold and blue
            string output = $"{agentDisplayName}\n";

            string outputSpeech = null;
            if (!string.IsNullOrEmpty(response.speech))
            {
                outputSpeech = response.speech;
                output += $"<b>Speech</b>: {outputSpeech}\n";
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
            if (chatOutput != null && outputSpeech != null) chatOutput.text += $"{agentDisplayName}\n{outputSpeech}\n";
            if (logOutput != null) logOutput.text += output;
        }

        public void AddToAuditoryLanguageBuffer(string inputText)
        {
            if (inputText == null) return;

            AuditoryInput inputItem = new AuditoryInput(AuditoryType.LANGUAGE, inputText);

            auditoryLanguageBufferList.Add(inputItem);
        }

        private void ResetGPUThrottling(int originalQualityLevel, int originalFrameRate)
        {
            if (toggleGPUThrottling)
            {
                // Restore the original render quality and frame rate on the main thread
                UnityMainThreadDispatcher.Instance().Enqueue(() =>
                {
                    QualitySettings.SetQualityLevel(originalQualityLevel);
                    Application.targetFrameRate = originalFrameRate;
                });
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
