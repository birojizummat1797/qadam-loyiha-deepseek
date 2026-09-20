import { create } from "zustand";
import { persist } from "zustand/middleware";

type State = {
  stage1ResultId: number | null;
  stage1Teaser: any | null;
  paid: boolean;
  setStage1: (id: number, teaser: any) => void;
  setPaid: (v: boolean) => void;
  reset: () => void;
};

export const useStore = create<State>()(
  persist(
    (set) => ({
      stage1ResultId: null,
      stage1Teaser: null,
      paid: false,
      setStage1: (id, teaser) =>
        set({ stage1ResultId: id, stage1Teaser: teaser }),
      setPaid: (v) => set({ paid: v }),
      reset: () =>
        set({ stage1ResultId: null, stage1Teaser: null, paid: false }),
    }),
    { name: "qadam-store" }
  )
);
