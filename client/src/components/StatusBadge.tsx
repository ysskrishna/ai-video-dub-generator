import { Clock, Loader2, CheckCircle2, XCircle } from "lucide-react";

interface StatusBadgeProps {
  status: "pending" | "processing" | "completed" | "failed";
}

export const StatusBadge = ({ status }: StatusBadgeProps) => {
  const variants = {
    pending: {
      icon: Clock,
      label: "Pending",
      className: "text-xs text-muted-foreground",
    },
    processing: {
      icon: Loader2,
      label: "Processing",
      className: "text-xs text-foreground",
    },
    completed: {
      icon: CheckCircle2,
      label: "Completed",
      className: "text-xs text-success",
    },
    failed: {
      icon: XCircle,
      label: "Failed",
      className: "text-xs text-destructive",
    },
  };

  const { icon: Icon, label, className } = variants[status];

  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <Icon className={`h-3.5 w-3.5 ${status === "processing" ? "animate-spin" : ""}`} />
      <span className="font-medium">{label}</span>
    </div>
  );
};
