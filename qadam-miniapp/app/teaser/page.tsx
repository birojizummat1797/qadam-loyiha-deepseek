"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/** DEPRECATED v0 screen (PM gate 2026-10-03): the live diagnostic is /discovery. */
export default function DeprecatedV0Page() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/discovery");
  }, [router]);
  return null;
}
