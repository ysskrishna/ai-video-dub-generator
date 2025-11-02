import { Link } from "react-router-dom";
import { Video } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex h-14 items-center">
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Video className="h-5 w-5" />
            <span className="font-semibold text-sm">AI Video Dub</span>
          </Link>
        </div>
      </nav>
    </header>
  );
}

