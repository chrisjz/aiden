using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using CandyCoded.env;
using UnityEngine.UI;

public class TextToSpeech : MonoBehaviour
{
    public TMP_Text requestText;
    public TMP_Text logOutput;


    private string apiURL;
    private AudioSource audioSource;

    private void Start()
    {
        // Check if Vocal API is enabled
        env.TryParseEnvironmentVariable("VOCAL_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Vocal API is disabled");
            if (logOutput != null) logOutput.text += $"<color=#FF9999>Vocal API is disabled</color>\n";
            return;
        }
        else
        {
            Debug.Log("Vocal API is enabled");
            if (logOutput != null) logOutput.text += $"<color=#99FF99>Vocal API is enabled</color>\n";
        }

        audioSource = gameObject.AddComponent<AudioSource>(); // Initialize the AudioSource component
    }

    public void SynthesizeAndPlay(Button button)
    {
        if (!audioSource)
        {
            return;
        }

        // Set API URL from environment variables
        if (env.TryParseEnvironmentVariable("VOCAL_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("VOCAL_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("VOCAL_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/api/tts";
            Debug.Log($"Vocal API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for vocal API URL.");
            return;
        }

        button.interactable = false;

        Debug.Log("Start speech synthesis.");
        StartCoroutine(SynthesizeSpeech(requestText.text, button));
    }

    private IEnumerator SynthesizeSpeech(string text, Button button)
    {
        string requestUrl = $"{apiURL}?text={UnityWebRequest.EscapeURL(text)}";

        using (UnityWebRequest www = UnityWebRequest.Get(requestUrl))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                // Load the audio data into an AudioClip
                AudioClip audioClip = WavUtility.ToAudioClip(www.downloadHandler.data);
                if (audioClip == null)
                {
                    Debug.LogError("Failed to convert response data to AudioClip.");
                }
                else
                {
                    if (audioSource.isPlaying)
                    {
                        audioSource.Stop();
                    }
                    audioSource.clip = audioClip;
                    audioSource.Play();
                }
            }
        }

        button.interactable = true;
    }
}
