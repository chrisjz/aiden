using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class AutoScrollManager : MonoBehaviour
{
    public ScrollRect scrollRect;        // The ScrollRect component of the Scroll View
    public TMP_Text targetText;          // The TMP_Text component to monitor
    public bool autoScrollEnabled = true; // Toggle for enabling/disabling auto-scroll

    private bool userScrolled = false;

    private void Start()
    {
        // Add listener to detect user scroll interaction
        scrollRect.onValueChanged.AddListener(OnScroll);

        // If auto-scrolling is enabled at the start, ensure we're at the bottom
        if (autoScrollEnabled)
        {
            ScrollToBottom();
        }
    }

    private void Update()
    {
        // If auto-scroll is enabled and user hasn't manually scrolled, keep scrolling to the bottom
        if (autoScrollEnabled && !userScrolled)
        {
            ScrollToBottom();
        }
    }

    // Called when the ScrollRect's value is changed (i.e., when the user scrolls)
    private void OnScroll(Vector2 position)
    {
        // If the user scrolls upwards, disable auto-scroll
        if (scrollRect.verticalNormalizedPosition > 0.001f) // Detect upward scrolling
        {
            userScrolled = true;
        }
        else
        {
            userScrolled = false; // At the bottom, re-enable auto-scroll
        }
    }

    // Call this function to manually scroll to the bottom
    public void ScrollToBottom()
    {
        Canvas.ForceUpdateCanvases(); // Ensure the canvas is updated
        scrollRect.verticalNormalizedPosition = 0f; // 0 means scroll to the bottom
        Canvas.ForceUpdateCanvases(); // Force canvas update to apply the change
    }

    // Enable auto-scroll (for example, if the user clicks a button to toggle it back on)
    public void EnableAutoScroll()
    {
        autoScrollEnabled = true;
        userScrolled = false;
        ScrollToBottom(); // Scroll to bottom immediately when re-enabled
    }

    // Disable auto-scroll
    public void DisableAutoScroll()
    {
        autoScrollEnabled = false;
    }
}
