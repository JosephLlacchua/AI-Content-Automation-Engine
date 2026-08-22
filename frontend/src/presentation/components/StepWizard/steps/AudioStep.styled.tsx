import React from 'react'
import styled, { keyframes } from 'styled-components'

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`

export const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0 4px;
`

export const ColLabel = styled.div`
  font-size: 11px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.textMuted};
  text-transform: uppercase;
  letter-spacing: 0.08em;
`

export const SceneList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  scrollbar-width: thin;
  padding-right: 4px;
`

export const SceneCard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(8px);
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: ${({ theme }) => theme.colors.accent}55;
    background: rgba(255, 255, 255, 0.035);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  }
`

export const NarrationRow = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
`

export const SceneNum = styled.span`
  font-size: 11px;
  font-weight: 800;
  color: ${({ theme }) => theme.colors.accentLight};
  background: ${({ theme }) => theme.colors.accent}22;
  border: 1px solid ${({ theme }) => theme.colors.accent}44;
  padding: 2px 7px;
  border-radius: 6px;
  flex-shrink: 0;
  line-height: 1.2;
  letter-spacing: 0.04em;
`

export const NarrationText = styled.p`
  margin: 0;
  font-size: 13.5px;
  line-height: 1.5;
  color: ${({ theme }) => theme.colors.text};
  font-weight: 400;
`

export const ControlsRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 10px;
`

export const AudioWrapper = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  flex: 1 1 280px;
  min-width: 200px;
  height: 36px;
`

export const AudioEl = styled.audio`
  width: 100%;
  height: 34px;
  accent-color: ${({ theme }) => theme.colors.accent};
  border-radius: 6px;
`

export const AudioLoadingBadge = styled.div`
  position: absolute;
  inset: 0;
  background: rgba(15, 15, 25, 0.85);
  backdrop-filter: blur(4px);
  border-radius: 6px;
  border: 1px solid ${({ theme }) => theme.colors.accent}66;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: ${({ theme }) => theme.colors.accentLight};
  font-size: 11px;
  font-weight: 600;
  animation: ${pulse} 1.5s infinite;
  z-index: 2;
`

export const Spinner = styled.div`
  width: 14px;
  height: 14px;
  border: 2px solid ${({ theme }) => theme.colors.accent}44;
  border-top-color: ${({ theme }) => theme.colors.accentLight};
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
`

export const PendingBar = styled.div`
  width: 100%;
  height: 34px;
  border-radius: 6px;
  border: 1px dashed ${({ theme }) => theme.colors.border};
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 8px;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 11px;
  opacity: 0.6;
  user-select: none;
`

/* ── SFX Controls Capsule ─────────────────────────────── */

export const SfxGroup = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid ${({ theme }) => theme.colors.border};
  padding: 3px 6px;
  border-radius: 8px;
`

export const SfxLabel = styled.span`
  font-size: 10px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.accentLight};
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0 4px;
  display: flex;
  align-items: center;
  gap: 4px;
`

export const SfxSelect = styled.select`
  height: 28px;
  border-radius: 6px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  background: ${({ theme }) => theme.colors.surface ?? '#16162a'};
  color: ${({ theme }) => theme.colors.text};
  font-size: 11.5px;
  padding: 0 8px;
  cursor: pointer;
  outline: none;
  color-scheme: dark;
  transition: border-color 0.15s, box-shadow 0.15s;

  &:hover {
    border-color: ${({ theme }) => theme.colors.accent};
  }
  &:focus {
    border-color: ${({ theme }) => theme.colors.accent};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.accent}33;
  }

  option {
    background: #181828;
    color: #ffffff;
  }
`

export const SfxIconBtn = styled.button<{ $loading?: boolean }>`
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  background: rgba(255, 255, 255, 0.04);
  color: ${({ theme }) => theme.colors.text};
  font-size: 13px;
  cursor: ${({ $loading }) => ($loading ? 'wait' : 'pointer')};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;

  &:hover:not(:disabled) {
    background: ${({ theme }) => theme.colors.accent}33;
    color: ${({ theme }) => theme.colors.accentLight};
    border-color: ${({ theme }) => theme.colors.accent};
    transform: translateY(-1px);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.35;
    cursor: not-allowed;
  }
`

export const SfxDivider = styled.div`
  width: 1px;
  height: 18px;
  background: ${({ theme }) => theme.colors.border};
  margin: 0 2px;
  opacity: 0.6;
`

/* ── Legacy exports (safety) ─────────────────────────── */
export const SceneRow = SceneCard
export const NarrationCell = NarrationRow
export const AudioCell = ControlsRow
export const AudioColumn = ControlsRow
export const SfxRow = ControlsRow
