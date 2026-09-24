"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
      }, 2000);
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
    5: "Zo'r!",
  };

  return (
    <>
      {/* Trigger */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-2xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/30 text-sm font-medium no-print"
        >
          <MessageSquare className="w-4 h-4 text-indigo-400" />
          Fikringizni bildiring
        </button>
      )}

      {/* Modal */}
      <AnimatePresence>
        {open && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm no-print">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full max-w-sm rounded-3xl bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/20 overflow-hidden"
            >
              {done ? (
                <div className="p-8 text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4"
                  >
                    <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                  </motion.div>
                  <h3 className="text-lg font-bold mb-2">Rahmat!</h3>
                  <p className="text-xs text-[var(--tg-hint)]">
                    Fikringiz biz uchun juda muhim. Bu mahsulotni
                    yaxshilashga yordam beradi.
                  </p>
                </div>
              ) : (
                <>
                  <div className="p-4 border-b border-[var(--tg-hint)]/15 flex items-center justify-between">
                    <h3 className="font-semibold">Fikringizni bildiring</h3>
                    <button
                      onClick={() => setOpen(false)}
                      className="w-8 h-8 rounded-full hover:bg-[var(--tg-bg)] flex items-center justify-center"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="p-5 space-y-4">
                    <div>
                      <p className="text-sm text-center mb-3">
                        Natijadan qanchalik mamnunmisiz?
                      </p>
                      <div className="flex justify-center gap-2">
                        {[1, 2, 3, 4, 5].map((s) => (
                          <button
                            key={s}
                            onClick={() => setRating(s)}
                            className="transition-transform hover:scale-110"
                          >
                            <Star
                              className={`w-9 h-9 ${
                                s <= rating
                                  ? "text-amber-400 fill-amber-400"
                                  : "text-[var(--tg-hint)]/30"
                              }`}
                            />
                          </button>
                        ))}
                      </div>
                      {rating > 0 && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-center text-sm font-medium mt-2 text-amber-400"
                        >
                          {LABELS[rating]}
                        </motion.p>
                      )}
                    </div>

                    <div>
                      <p className="text-xs text-[var(--tg-hint)] mb-2">
                        Izoh (ixtiyoriy)
                      </p>
                      <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value.slice(0, 500))}
                        placeholder="Nima yaxshi boldi, nima yaxshilanishi kerak?"
                        className="w-full p-3 rounded-xl bg-[var(--tg-bg)] border border-[var(--tg-hint)]/20 text-sm resize-none focus:outline-none focus:border-indigo-500"
                        rows={3}
                      />
                      <p className="text-[10px] text-[var(--tg-hint)] text-right mt-1">
                        {comment.length}/500
                      </p>
                    </div>
                  </div>

                  <div className="p-4 border-t border-[var(--tg-hint)]/15">
                    <button
                      onClick={handleSubmit}
                      disabled={rating < 1 || submitting}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-40"
                    >
                      {submitting ? (
                        "Yuborilmoqda..."
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          Yuborish
                        </>
                      )}
                    </button>
                  </div>
                </>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
