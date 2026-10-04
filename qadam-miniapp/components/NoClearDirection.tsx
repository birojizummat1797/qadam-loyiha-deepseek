/**
 * Honest result when no career reaches the minimum score (BL-14, Founder decision 2026-10-04).
 * The list is never padded: 5 is a ceiling, not a quota. Text: Founder's words (decision record).
 */
import { Compass } from "lucide-react";

// The careers catalog page is not live yet; the link appears once its URL is configured.
const CATALOG_URL = process.env.NEXT_PUBLIC_CATALOG_URL || "";

export function NoClearDirection() {
  return (
    <div className="card-clean mb-6" data-testid="no-clear-direction">
      <div className="flex items-start gap-3">
        <Compass className="w-5 h-5 text-subtle shrink-0 mt-0.5" />
        <div>
          <p className="t-heading mb-2">Hozircha javoblaringiz bo&apos;yicha aniq yo&apos;nalish ko&apos;rinmayapti.</p>
          <p className="t-small text-muted mb-2">
            Qadam&apos;ning birinchi bosqichida faqat IT va zamonaviy kasblar — raqamli texnologiyalar bilan
            bog&apos;liq yo&apos;nalishlar — tanlab olingan. Agar aynan shu sohalarga qiziqsangiz va mutaxassis
            bo&apos;lishni maqsad qilgan bo&apos;lsangiz, keyinroq yana bir urinib ko&apos;ring.
          </p>
          {CATALOG_URL && (
            <p className="t-small">
              <a href={CATALOG_URL} target="_blank" rel="noopener noreferrer" className="text-primary underline">
                Hozirgi yo&apos;nalishlarimiz bilan tanishib chiqing
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
