using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;

public class BrainController : MonoBehaviour
{
    [Header("Agent Profile")]
    public string agentId = "1";
    public string agentName = "AIden";

    [Header("Configuration")]
    public string configPath = "./config/brain/default.json";

    [Header("Cycle Settings")]
    public float cycleTime = 1.0f; // Default to 1 second, can be overridden by an environment variable

    private AuditoryAPIClient auditoryApiClient;
    private VisionAPIClient visionApiClient;
    private string corticalApiUrl;

    private bool isAuditoryApiEnabled = false;
    private bool isVisionApiEnabled = false;

    private void Start()
    {
        // Find the AI audio capture (ear sensor) in child GameObjects
        AIAudioCapture audioCapture = GetComponentInChildren<AIAudioCapture>();

        // Find the camera (eye sensor) in child GameObjects
        Camera cameraCapture = GetComponentInChildren<Camera>();

        // Initialize API clients
        auditoryApiClient = new AuditoryAPIClient(audioCapture);
        visionApiClient = new VisionAPIClient(cameraCapture);

        // Check if APIs are enabled
        isAuditoryApiEnabled = auditoryApiClient.IsAPIEnabled();
        isVisionApiEnabled = visionApiClient.IsAPIEnabled();

        if (!isAuditoryApiEnabled && !isVisionApiEnabled)
        {
            Debug.LogError("No sensor APIs are enabled. At least one sensor is required for cortical processing.");
            return;
        }

        // Set the Cortical API URL
        if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
        {
            corticalApiUrl = $"{protocol}://{host}:{port}/cortical";
            Debug.Log($"Cortical API URL set to: {corticalApiUrl}");
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
        while (true)
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
        if (isVisionApiEnabled)
        {
            yield return StartCoroutine(visionApiClient.GetVisionDataCoroutine(
                occipitalData => sensoryInput.vision.Add(new VisionInput { type = "general", content = occipitalData }),
                error => Debug.LogError(error)
            ));
        }

        // Step 2: Fetch Auditory Data (Ambient Noise) if enabled
        if (isAuditoryApiEnabled)
        {
            yield return StartCoroutine(auditoryApiClient.GetAuditoryDataCoroutine(
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
        UnityWebRequest corticalRequest = new UnityWebRequest(corticalApiUrl, "POST")
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
