using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Collections;
using TMPro;
using CandyCoded.env;
using UnityEngine.UI;

public class AuditoryAmbientAPIIntegration : MonoBehaviour
{
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL;

    private void Start()
    {
        // Check if Auditory Ambient API is enabled
        env.TryParseEnvironmentVariable("AUDITORY_AMBIENT_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Auditory Ambient API is disabled");
            return;
        }
        else
        {
            Debug.Log("Auditory Ambient API is enabled");
        }

        // Set API URL from environment variables to point to the occipital endpoint
        if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/auditory";
            Debug.Log($"Brain API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
            return;
        }

        sendButton.onClick.AddListener(SendRequestToAuditoryAmbientAPI);
    }

    private void SendRequestToAuditoryAmbientAPI()
    {
        sendButton.interactable = false;

        // TODO: Get audio recording from auditory sensor
        string audioFilePath = "./Assets/Project/Sfx/birds-chirping-75156.mp3";

        byte[] audioData = System.IO.File.ReadAllBytes(audioFilePath);
        string base64audio = Convert.ToBase64String(audioData);

        Debug.Log("Start auditory ambient inference.");
        StartCoroutine(StreamRequest(base64audio));
    }

    private IEnumerator StreamRequest(string base64audio)
    {
        var json = JsonUtility.ToJson(new AuditoryRequest { audio = base64audio });
        var request = new UnityWebRequest(apiURL, "POST")
        {
            uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json)),
            downloadHandler = new DownloadHandlerBuffer()
        };
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            string responseString = request.downloadHandler.text;
            Debug.Log("Response: " + responseString);
            UpdateResponseText(responseString);
        }
        else
        {
            Debug.LogError("Error: " + request.error);
        }

        sendButton.interactable = true;
    }


    private void UpdateResponseText(string text)
    {
        responseText.text = text;
    }
}

// Define classes to match the JSON structure of the response
[Serializable]
public class AuditoryRequest
{
    public string audio;
}
