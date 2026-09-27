"use client";

import { useState } from "react";
import { Star, MessageSquare, Send, CheckCircle2, X } from "lucide-react";
import { submitFeedback } from "@/lib/api";

export function FeedbackModal({
  reportId,
  onClose,
}: {
  reportId: number;
  onClose?: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async () => {
    if (rating < 1) return;
    setSubmitting(true);
    try {
      await submitFeedback(reportId, rating, comment);
      setDone(true);
      setTimeout(() => {
        setOpen(false);
        onClose?.();
      }, 1500);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  const LABELS: { [key: number]: string } = {
    1: "Yomon",
    2: "Qoniqarli emas",
    3: "O'rtacha",
    4: "Yaxshi",
    5: "Zo'r",
  };

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="btn btn-secondary no-print"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Fikringizni bildiring</span>
        </button>
      )}

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 no-print">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
            {done ? (
              <div className="p-10 text-center">
                <div className="w-14 h-14 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-4">
                  <CheckCircle2 className="w-7 h-7 text-success" />
                </div>
                <h3 className="t-heading mb-2">Rahmat!</h3>
                <p className="t-small text-muted">
                  Fikringiz mahsulotni yaxshilashga yordam beradi.
                </p>
              </div>
            ) : (
              <>
                <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between">
                  <h3 className="t-heading">Fikringizni bildiring</h3>
                  <button
                    onClick={() => setOpen(false)}
                    className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="p-5 space-y-5">
                  <div>
                    <p className="t-small text-center mb-4">
                      Natijadan qanchalik mamnunmisiz?
                    </p>
                    <div className="flex justify-center gap-2">
                      {[1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          onClick={() => setRating(s)}
                          className="p-1"
                        >
                          <Star
                            className={`w-8 h-8 transition-colors ${
                              s <= rating
                                ? "text-warning fill-warning"
                                : "text-subtle"
                            }`}
                          />
                        </button>
                      ))}
                    </div>
                    {rating > 0 && (
                      <p className="t-small text-warning text-center mt-2 font-medium">
                        {LABELS[rating]}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="t-caption text-subtle mb-2">
                      Izoh (ixtiyoriy)
                    </p>
                    <textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value.slice(0, 500))}
                      placeholder="Nima yaxshi, nima yaxshilanishi kerak?"
                      className="w-full p-3 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)] t-small resize-none focus:outline-none focus:border-primary"
                      rows={3}
                    />
                    <p className="t-caption text-subtle text-right mt-1">
                      {comment.length}/500
                    </p>
                  </div>
                </div>

                <div className="p-4 pt-0">
                  <button
                    onClick={handleSubmit}
                    disabled={rating < 1 || submitting}
                    className="btn btn-primary"
                  >
                    {submitting ? (
                      "Yuborilmoqda..."
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Yuborish</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
