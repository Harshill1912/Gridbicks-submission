// One hook per endpoint. Data never changes, so results are cached for the session.
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

const forever = { staleTime: Infinity, gcTime: Infinity };

export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: api.health, ...forever });

export const useSeries = (day: string, cutoff: string) =>
  useQuery({ queryKey: ["series", day, cutoff], queryFn: () => api.series(day, cutoff), enabled: !!day, ...forever });

export const useSummary = (cutoff: string) =>
  useQuery({ queryKey: ["summary", cutoff], queryFn: () => api.summary(cutoff), ...forever });

export const useByHorizon = () => useQuery({ queryKey: ["horizon"], queryFn: api.byHorizon, ...forever });

export const useByHour = (cutoff: string) =>
  useQuery({ queryKey: ["hour", cutoff], queryFn: () => api.byHour(cutoff), ...forever });

export const useByWindLevel = (cutoff: string) =>
  useQuery({ queryKey: ["level", cutoff], queryFn: () => api.byWindLevel(cutoff), ...forever });

export const useScatter = (cutoff: string) =>
  useQuery({ queryKey: ["scatter", cutoff], queryFn: () => api.scatter(cutoff), ...forever });

export const usePlan = (day: string, confidence: number, cutoff: string) =>
  useQuery({
    queryKey: ["plan", day, confidence, cutoff],
    queryFn: () => api.plan(day, confidence, cutoff),
    enabled: !!day,
    placeholderData: (prev) => prev, // keep the chart steady while the slider moves
    ...forever,
  });

export const useBacktest = (confidence: number, cutoff: string) =>
  useQuery({
    queryKey: ["backtest", confidence, cutoff],
    queryFn: () => api.backtest(confidence, cutoff),
    placeholderData: (prev) => prev,
    ...forever,
  });
