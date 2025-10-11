import { useState, useEffect } from "react";
import { Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { api, LanguagesResponse, JobStatus } from "@/lib/api";
import { JobCard } from "@/components/JobCard";

const Home = () => {
  const [videoUrl, setVideoUrl] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("");
  const [languages, setLanguages] = useState<LanguagesResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<number | null>(null);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const { toast } = useToast();

  // Fetch available languages
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const data = await api.getLanguages();
        setLanguages(data);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load languages. Please refresh the page.",
          variant: "destructive",
        });
      }
    };
    fetchLanguages();
  }, [toast]);

  // Fetch all jobs
  const fetchJobs = async () => {
    try {
      const data = await api.getAllJobs();
      setJobs(data.sort((a, b) => b.job_id - a.job_id));
    } catch (error) {
      console.error("Error fetching jobs:", error);
    } finally {
      setIsLoadingJobs(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  // Poll current job status
  useEffect(() => {
    if (!currentJobId) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await api.getJobStatus(currentJobId);
        
        // Update jobs list
        setJobs((prevJobs) => {
          const existingIndex = prevJobs.findIndex((j) => j.job_id === status.job_id);
          if (existingIndex >= 0) {
            const updated = [...prevJobs];
            updated[existingIndex] = status;
            return updated;
          }
          return [status, ...prevJobs];
        });

        if (status.status === "completed" || status.status === "failed") {
          clearInterval(pollInterval);
          setCurrentJobId(null);
          toast({
            title: status.status === "completed" ? "Success!" : "Failed",
            description:
              status.status === "completed"
                ? "Your dubbed video is ready to download!"
                : "Video dubbing failed. Please try again.",
            variant: status.status === "completed" ? "default" : "destructive",
          });
        }
      } catch (error) {
        console.error("Error polling job status:", error);
      }
    }, 3000);

    return () => clearInterval(pollInterval);
  }, [currentJobId, toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!videoUrl.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter a video URL",
        variant: "destructive",
      });
      return;
    }

    if (!targetLanguage) {
      toast({
        title: "Validation Error",
        description: "Please select a target language",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.createJob({
        video_url: videoUrl,
        target_language: targetLanguage,
      });

      setCurrentJobId(response.job_id);
      
      // Add new job to the list
      const newJob: JobStatus = {
        job_id: response.job_id,
        video_url: videoUrl,
        target_language: targetLanguage,
        status: response.status as JobStatus["status"],
        error_code: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setJobs((prev) => [newJob, ...prev]);

      toast({
        title: "Job Created!",
        description: response.message,
      });

      // Clear form
      setVideoUrl("");
      setTargetLanguage("");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create dubbing job. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = (jobId: number) => {
    window.open(api.getDownloadUrl(jobId), "_blank");
  };

  const handleRefresh = async () => {
    setIsLoadingJobs(true);
    await fetchJobs();
    toast({
      title: "Refreshed",
      description: "Job list updated",
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12">
      {/* Create Section */}
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Create Dubbed Video</h1>
          <p className="text-sm text-muted-foreground">
            Enter a video URL and select your target language
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="video-url">Video URL</Label>
            <Input
              id="video-url"
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              disabled={isSubmitting}
              aria-label="Enter video URL"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="language">Target Language</Label>
            <Select
              value={targetLanguage}
              onValueChange={setTargetLanguage}
              disabled={isSubmitting || !languages}
            >
              <SelectTrigger id="language" aria-label="Select target language">
                <SelectValue placeholder="Select a language" />
              </SelectTrigger>
              <SelectContent className="max-h-60">
                {languages &&
                  Object.entries(languages.languages).map(([name, code]) => (
                    <SelectItem key={code} value={code}>
                      {name}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full"
            aria-label="Generate dubbed video"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating Job...
              </>
            ) : (
              "Generate Dubbed Video"
            )}
          </Button>
        </form>
      </div>

      <Separator />

      {/* History Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold tracking-tight">Recent Jobs</h2>
            <p className="text-sm text-muted-foreground">
              View and manage your dubbing jobs
            </p>
          </div>
          <Button
            onClick={handleRefresh}
            disabled={isLoadingJobs}
            variant="outline"
            size="sm"
            aria-label="Refresh job list"
          >
            <RefreshCw className={`h-4 w-4 ${isLoadingJobs ? "animate-spin" : ""}`} />
          </Button>
        </div>

        {isLoadingJobs ? (
          <div className="text-sm text-muted-foreground text-center py-8">
            Loading jobs...
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-8 border border-dashed border-border rounded-lg">
            No jobs yet. Create your first dubbed video above.
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {jobs.map((job) => (
              <JobCard key={job.job_id} job={job} onDownload={handleDownload} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
