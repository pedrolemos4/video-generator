using System.Text;
using System.Text.Json;
using System.Diagnostics;

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("=== Video Generator ===");

        string storyPath = args.Length > 0 ? args[0] : "stories/1.json";
        Console.WriteLine($"Story file: {storyPath}");

        Directory.CreateDirectory("tmp");
        Directory.CreateDirectory("output");

        // 1. Load story from JSON
        var segments = GenerateStoryFromFile(storyPath);

        // 2. Build subtitles
        string srtPath = "tmp/subtitles.srt";
        BuildSubtitles(segments, srtPath);

        // 3. Render video
        string inputVideo = "assets/video.mp4";
        string audio = "assets/voice.wav";
        string outputVideo = $"output/result_{DateTime.Now:yyyyMMdd_HHmmss}.mp4";

        await RenderVideo(inputVideo, audio, srtPath, outputVideo);

        Console.WriteLine("Done!");
        Console.WriteLine($"Output: {outputVideo}");
    }

    // ------------------------

    static List<StorySegment> GenerateStoryFromFile(string path)
    {
        if (!File.Exists(path))
            throw new FileNotFoundException($"Story file not found: {path}");

        var json = File.ReadAllText(path);

        var story = JsonSerializer.Deserialize<StoryFile>(
            json,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        if (story == null || string.IsNullOrWhiteSpace(story.Content))
            throw new Exception("Invalid story file");

        Console.WriteLine($"Loaded story: {story.Title}");

        // Split content into sentences
        var sentences = story.Content
            .Split(new[] { '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries)
            .Select(s => s.Trim())
            .Where(s => s.Length > 0)
            .ToList();

        var segments = new List<StorySegment>();

        foreach (var sentence in sentences)
        {
            // Rough speaking rate: ~150 wpm ≈ 0.4 sec per word
            int wordCount = sentence.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length;
            double seconds = Math.Max(1.5, wordCount * 0.4);

            segments.Add(new StorySegment(sentence + ".", seconds));
        }

        return segments;
    }

    static void BuildSubtitles(List<StorySegment> segments, string path)
    {
        var sb = new StringBuilder();
        TimeSpan cursor = TimeSpan.Zero;
        int index = 1;

        foreach (var s in segments)
        {
            var start = cursor;
            var end = cursor + TimeSpan.FromSeconds(s.Seconds);

            sb.AppendLine(index.ToString());
            sb.AppendLine($"{FormatTime(start)} --> {FormatTime(end)}");
            sb.AppendLine(s.Text);
            sb.AppendLine();

            cursor = end;
            index++;
        }

        File.WriteAllText(path, sb.ToString());
        Console.WriteLine($"Subtitles written to {path}");
    }

    static async Task RenderVideo(
        string video,
        string audio,
        string subtitles,
        string output)
    {
        Console.WriteLine("Rendering video...");

        var args =
            $"-y " +
            $"-i \"{video}\" " +
            $"-i \"{audio}\" " +
            $"-vf \"subtitles={subtitles}\" " +
            $"-c:v libx264 " +
            $"-c:a aac " +
            $"-shortest " +
            $"\"{output}\"";

        var psi = new ProcessStartInfo
        {
            FileName = "ffmpeg",
            Arguments = args,
            RedirectStandardError = true,
            UseShellExecute = false
        };

        using var process = Process.Start(psi)!;

        // FFmpeg logs to stderr
        while (!process.StandardError.EndOfStream)
        {
            var line = await process.StandardError.ReadLineAsync();
            if (!string.IsNullOrWhiteSpace(line))
                Console.WriteLine(line);
        }

        await process.WaitForExitAsync();

        if (process.ExitCode != 0)
            throw new Exception("FFmpeg failed");

        Console.WriteLine("Rendering complete");
    }

    static string FormatTime(TimeSpan t)
    {
        return $"{t.Hours:00}:{t.Minutes:00}:{t.Seconds:00},{t.Milliseconds:000}";
    }
}

// ------------------------
// Models

record StoryFile(string Title, string Content);

record StorySegment(string Text, double Seconds);
