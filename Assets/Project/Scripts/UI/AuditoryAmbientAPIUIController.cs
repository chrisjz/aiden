using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class AuditoryAmbientAPIUIController : MonoBehaviour
{
    public TMP_Text responseText;
    public Button sendButton;
    public bool saveCapturedAudio = false;

    public AIAudioCapture audioCapture; // Reference to the AIAudioCapture script

    private AuditoryAPIClient auditoryApiClient;

    private void Start()
    {
        auditoryApiClient = new AuditoryAPIClient();

        if (!auditoryApiClient.IsAPIEnabled())
        {
            Debug.Log("Auditory Ambient API is disabled or not configured.");
            return;
        }

        sendButton.onClick.AddListener(OnSendButtonClicked);
    }

    private void OnSendButtonClicked()
    {
        sendButton.interactable = false;

        // Get the last second of audio data from the audio capture component
        float[] lastSecondAudioData = audioCapture.GetLastSecondAudio();

        // Downsample to 16,000 Hz
        float[] downsampledData = auditoryApiClient.DownsampleAudio(lastSecondAudioData, AudioSettings.outputSampleRate, 16000);

        // Convert downsampled audio data to WAV format
        byte[] wavData = auditoryApiClient.ConvertToWav(downsampledData, 16000);

        // Save the audio data if toggled on
        auditoryApiClient.SaveAudioToFile(wavData, saveCapturedAudio);

        // Convert the byte array to Base64
        string base64audio = Convert.ToBase64String(wavData);

        Debug.Log("Start auditory ambient inference.");
        StartCoroutine(auditoryApiClient.SendRequestToAuditoryAPI(base64audio, UpdateResponseText));
    }

    private void UpdateResponseText(string text)
    {
        responseText.text = text;
        sendButton.interactable = true;
    }
}

// Define classes to match the JSON structure of the request
[Serializable]
public class AuditoryRequest
{
    public string audio;
}
