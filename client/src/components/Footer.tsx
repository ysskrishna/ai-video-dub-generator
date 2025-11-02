import { FaGithub, FaLinkedin, FaYoutube, FaProductHunt } from "react-icons/fa";

export function Footer() {
  return (
    <footer className="py-2 md:py-4">
      <div className="w-full flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-4 md:px-6">
        <a
          href="https://github.com/ysskrishna"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-4 hover:opacity-80 transition-opacity"
        >
          <img
            src="https://github.com/ysskrishna.png"
            alt="Y. Siva Sai Krishna"
            width={40}
            height={40}
            className="rounded-full"
          />
          <div>
            <p className="font-medium">Y. Siva Sai Krishna</p>
            <p className="text-sm text-muted-foreground">@ysskrishna</p>
          </div>
        </a>

        <div className="flex items-center gap-4">
          <a
            href="https://github.com/ysskrishna"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <FaGithub className="h-5 w-5" />
            <span className="sr-only">GitHub</span>
          </a>

          <a
            href="https://linkedin.com/in/ysskrishna"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <FaLinkedin className="h-5 w-5" />
            <span className="sr-only">LinkedIn</span>
          </a>
          <a
            href="https://www.youtube.com/@ysskrishna"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <FaYoutube className="h-5 w-5" />
            <span className="sr-only">YouTube</span>
          </a>
          <a
            href="https://www.producthunt.com/@ysskrishna"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <FaProductHunt className="h-5 w-5" />
            <span className="sr-only">Product Hunt</span>
          </a>
        </div>
      </div>
    </footer>
  );
}
