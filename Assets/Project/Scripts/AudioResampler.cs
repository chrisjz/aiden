using UnityEngine;

public static class AudioResampler
{
    public static AudioClip Resample(AudioClip clip, int targetSampleRate)
    {
        int sourceSampleRate = clip.frequency;
        float resampleRatio = (float)targetSampleRate / sourceSampleRate;

        int newSampleCount = Mathf.CeilToInt(clip.samples * resampleRatio);
        float[] sourceData = new float[clip.samples];
        float[] resampledData = new float[newSampleCount];

        clip.GetData(sourceData, 0);

        for (int i = 0; i < newSampleCount; i++)
        {
            float sourceIndex = i / resampleRatio;
            int lowerIndex = Mathf.FloorToInt(sourceIndex);
            int upperIndex = Mathf.Min(Mathf.CeilToInt(sourceIndex), sourceData.Length - 1);
            float lerpFactor = sourceIndex - lowerIndex;

            resampledData[i] = Mathf.Lerp(sourceData[lowerIndex], sourceData[upperIndex], lerpFactor);
        }

        AudioClip resampledClip = AudioClip.Create("ResampledClip", newSampleCount, 1, targetSampleRate, false);
        resampledClip.SetData(resampledData, 0);

        return resampledClip;
    }
}
