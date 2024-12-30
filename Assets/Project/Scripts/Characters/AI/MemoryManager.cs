using System;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using CandyCoded.env;
using TMPro;

public class MemoryManager : MonoBehaviour
{
    [Header("Agent Configuration")]
    [Tooltip("Dropdown containing agent IDs and names in the format 'ID: NAME'.")]
    public TMP_Dropdown agentSelectorDropdown;

    [Header("Output")]
    [Tooltip("Log output to display AI output.")]
    public TMP_Text logOutput;

    private string apiURL;

    private void Start()
    {

        // Set API URL from environment variables to point to the neuralyzer endpoint
        if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/neuralyzer/";
            Debug.Log($"Occipital endpoint URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
        }
    }

    public async void OnWipeShortTermMemoryButtonClicked(Button wipeMemoryButton)
    {
        // Disable the button while processing
        wipeMemoryButton.interactable = false;

        try
        {
            // Get the selected agent ID from the dropdown
            string selectedAgentId = GetSelectedAgentId();
            if (string.IsNullOrEmpty(selectedAgentId))
            {
                throw new Exception("No valid agent ID selected.");
            }

            // Call the API to wipe memory
            string response = await WipeShortTermMemory(selectedAgentId);

            // Update the UI with the response
            if (logOutput != null) logOutput.text += $"<color=#C0C0C0>Agent's short term memory wiped.</color>\n";
        }
        catch (Exception ex)
        {
            // Handle errors and display them
            Debug.LogError($"Error during neuralyzer API call: {ex.Message}");
            if (logOutput != null) logOutput.text += "<color=#FF9999>An error occurred when attempting to wipe the agent's short term memory.</color>\n";
        }
        finally
        {
            // Re-enable the button
            wipeMemoryButton.interactable = true;
        }
    }

    private string GetSelectedAgentId()
    {
        if (agentSelectorDropdown == null || agentSelectorDropdown.options.Count == 0)
        {
            Debug.LogError("Agent selector dropdown is not set or contains no options.");
            return null;
        }

        // Get the currently selected option
        string selectedOption = agentSelectorDropdown.options[agentSelectorDropdown.value].text;

        // Extract the agent ID from the format "ID: Name"
        string[] parts = selectedOption.Split(':');
        if (parts.Length > 1)
        {
            return parts[0].Trim(); // Return the ID part
        }

        Debug.LogError("Invalid format for agent dropdown value. Expected format 'ID: NAME'.");
        return null;
    }

    public async Task<string> WipeShortTermMemory(string agentId)
    {
        if (string.IsNullOrEmpty(agentId))
        {
            throw new ArgumentException("Agent ID cannot be null or empty.");
        }

        Debug.Log($"Wiping short term memory for agent: {agentId}");

        // Construct the request payload
        var payload = new NeuralyzerRequest { agent_id = agentId };
        string payloadJson = JsonUtility.ToJson(payload);

        using (UnityWebRequest request = new UnityWebRequest(apiURL, "POST"))
        {
            // Set up the request headers and body
            byte[] bodyRaw = Encoding.UTF8.GetBytes(payloadJson);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            // Send the request
            var operation = request.SendWebRequest();

            // Await the completion of the request
            while (!operation.isDone)
            {
                await Task.Yield();
            }

            // Check for errors
            if (request.result != UnityWebRequest.Result.Success)
            {
                throw new Exception($"Request failed: {request.error}");
            }

            // Return the response as a string
            return request.downloadHandler.text;
        }
    }

    [Serializable]
    public class NeuralyzerRequest
    {
        public string agent_id;
    }
}
