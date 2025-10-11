import { Download, ExternalLink, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "./StatusBadge";
import { JobStatus } from "@/lib/api";
import { format } from "date-fns";

interface JobCardProps {
  job: JobStatus;
  onDownload?: (jobId: number) => void;
}

export const JobCard = ({ job, onDownload }: JobCardProps) => {
  const formattedDate = format(new Date(job.created_at), "MMM d, yyyy 'at' h:mm a");

  return (
    <div className="border border-border rounded-lg p-4 hover:border-foreground/20 transition-colors bg-card">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="text-sm font-medium">Job #{job.job_id}</div>
        <StatusBadge status={job.status} />
      </div>

      <div className="space-y-3">
        <div className="flex items-start gap-2">
          <ExternalLink className="h-3.5 w-3.5 text-muted-foreground mt-0.5 flex-shrink-0" />
          <a
            href={job.video_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-muted-foreground hover:text-foreground line-clamp-1 break-all transition-colors"
            aria-label={`Open video ${job.job_id} in new tab`}
          >
            {job.video_url}
          </a>
        </div>

        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>{formattedDate}</span>
          </div>
          <div className="text-foreground font-medium">
            {job.target_language.toUpperCase()}
          </div>
        </div>

        {job.error_code && (
          <div className="text-xs text-destructive">
            Error: {job.error_code}
          </div>
        )}

        {job.status === "completed" && onDownload && (
          <Button
            onClick={() => onDownload(job.job_id)}
            size="sm"
            className="w-full"
            aria-label={`Download dubbed video ${job.job_id}`}
          >
            <Download className="h-3.5 w-3.5 mr-1.5" />
            Download
          </Button>
        )}
      </div>
    </div>
  );
};
