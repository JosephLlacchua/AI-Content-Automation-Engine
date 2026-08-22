import React, { useCallback, useEffect, useRef, useState, useMemo } from 'react'
import { PipelineLevel } from '../../../tools/types'
import Terminal from '../components/Terminal/Terminal'
import { ActionRow, BtnPrimary, BtnSecondary } from '../StepWizard.styled'
import { JobStep } from '../../../tools/hooks/useJobStep'
import {
  Header, ColLabel, SceneList, SceneCard,
  NarrationRow, SceneNum, NarrationText,
  ControlsRow, AudioWrapper, AudioEl, AudioLoadingBadge,
  Spinner, PendingBar, SfxGroup, SfxSelect,
  SfxIconBtn, SfxDivider, SfxLabel,
} from './AudioStep.styled'

// ── Types ────────────────────────────────────────────────
interface Scene { scene_number: number; narration: string; sfx_tag: string }
type SfxCatalog = Record<string, string[]>

// ── Hooks ────────────────────────────────────────────────
function useScript(url: string) {
  const [scenes, setScenes] = useState<Scene[]>([])
  useEffect(() => {
    fetch(url)
      .then(r => r.json())
      .then((d: { scenes: Scene[] }) => setScenes(d.scenes ?? []))
      .catch(() => {})
  }, [url])
  return scenes
}

function useAudioFiles(url: string, enabled: boolean) {
  const [files, setFiles] = useState<string[]>([])
  const reload = useCallback(() => {
    if (!enabled) return
    fetch(`${url}/audios`)
      .then(r => r.json())
      .then(d => setFiles(d as string[]))
      .catch(() => {})
  }, [url, enabled])
  useEffect(() => { reload() }, [reload])
  return { files, reload }
}

function useSfxCatalog(apiBase: string) {
  const [catalog, setCatalog] = useState<SfxCatalog>({})
  useEffect(() => {
    fetch(`${apiBase}/api/sfx`)
      .then(r => r.json())
      .then(d => setCatalog(d as SfxCatalog))
      .catch(() => {})
  }, [apiBase])
  return catalog
}

// ── SFX Scene Control ────────────────────────────────────
interface SfxControlProps {
  scene: Scene
  catalog: SfxCatalog
  apiBase: string
  ideaBase: string
  isMixing: boolean
  onRerollStart: (sceneNum: number) => void
  onRerollDone: (sceneNum: number) => void
}

function SfxControl({
  scene,
  catalog,
  apiBase,
  ideaBase,
  isMixing,
  onRerollStart,
  onRerollDone,
}: SfxControlProps) {
  const tags = Object.keys(catalog)
  const initialTag = scene.sfx_tag ?? 'none'
  const [selectedTag, setSelectedTag] = useState(initialTag)
  const [selectedFile, setSelectedFile] = useState('')
  const prevTagRef = useRef<string>(initialTag)
  const previewRef = useRef<HTMLAudioElement>(null)

  // Only reset the file selector when the TAG actually changes (not on catalog reloads)
  useEffect(() => {
    if (selectedTag === 'none') {
      prevTagRef.current = selectedTag
      setSelectedFile('')
      return
    }
    if (selectedTag !== prevTagRef.current) {
      // Tag changed: reset to first file in new category
      const files = catalog[selectedTag] ?? []
      setSelectedFile(files[0] ?? '')
      prevTagRef.current = selectedTag
    } else if (selectedFile === '' && catalog[selectedTag]?.length) {
      // Initial load: pick first available file
      setSelectedFile(catalog[selectedTag][0])
    }
  }, [selectedTag, catalog])

  const files = catalog[selectedTag] ?? []
  const previewUrl = (selectedTag !== 'none' && selectedFile)
    ? `${apiBase}/api/sfx/${selectedTag}/${encodeURIComponent(selectedFile)}/stream`
    : ''

  const handleApply = async () => {
    onRerollStart(scene.scene_number)
    try {
      await fetch(`${ideaBase}/sfx/scene`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_number: scene.scene_number,
          sfx_tag: selectedTag,
          sfx_file: selectedTag === 'none' ? '' : selectedFile,
        }),
      })
      onRerollDone(scene.scene_number)
    } catch {
      onRerollDone(scene.scene_number)
    }
  }

  const handlePlay = () => {
    if (previewRef.current && previewUrl) {
      previewRef.current.src = previewUrl
      previewRef.current.play()
    }
  }

  return (
    <SfxGroup>
      <audio ref={previewRef} style={{ display: 'none' }} />
      <SfxLabel>🔊 SFX</SfxLabel>
      <SfxSelect
        value={selectedTag}
        onChange={e => setSelectedTag(e.target.value)}
        title="Categoría de efecto de sonido"
      >
        <option value="none">🚫 Sin efecto</option>
        {tags.map(t => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </SfxSelect>

      <SfxSelect
        value={selectedFile}
        onChange={e => setSelectedFile(e.target.value)}
        disabled={selectedTag === 'none'}
        title="Archivo de sonido"
      >
        {selectedTag === 'none' ? (
          <option value="">(Ninguno)</option>
        ) : (
          files.map(f => (
            <option key={f} value={f}>
              {f}
            </option>
          ))
        )}
      </SfxSelect>

      <SfxIconBtn
        type="button"
        onClick={handlePlay}
        disabled={selectedTag === 'none' || !selectedFile || isMixing}
        title="Escuchar muestra de SFX"
      >
        ▶
      </SfxIconBtn>

      <SfxDivider />

      <SfxIconBtn
        type="button"
        onClick={handleApply}
        disabled={isMixing || (selectedTag !== 'none' && !selectedFile)}
        $loading={isMixing}
        title={selectedTag === 'none' ? 'Quitar SFX de esta escena' : 'Aplicar este SFX a la escena'}
      >
        {isMixing ? '⏳' : selectedTag === 'none' ? '🗑️' : '🎲'}
      </SfxIconBtn>
    </SfxGroup>
  )
}

// ── Main Component ───────────────────────────────────────
interface Props {
  base: string
  level: PipelineLevel
  jobStep: JobStep
  onGenerate: () => void
}

export default function AudioStep({ base, level, jobStep, onGenerate }: Props) {
  const apiBase = base.split('/api/')[0]
  const scenes = useScript(base + '/script')
  const { files: audioFiles, reload } = useAudioFiles(base, level >= 3)
  const catalog = useSfxCatalog(apiBase)
  const generated = level >= 3

  const [mixingScene, setMixingScene] = useState<number | null>(null)
  const [audioVersions, setAudioVersions] = useState<Record<number, number>>({})

  const handleRerollStart = (sceneNum: number) => {
    setMixingScene(sceneNum)
  }

  const handleRerollDone = (sceneNum: number) => {
    setMixingScene(null)
    setAudioVersions(prev => ({ ...prev, [sceneNum]: Date.now() }))
    reload()
  }

  if (jobStep.jobId) return <Terminal logs={jobStep.logs} running />

  return (
    <>
      <ActionRow>
        {generated ? (
          <BtnSecondary onClick={onGenerate}>↺ Regenerar Audio</BtnSecondary>
        ) : (
          <BtnPrimary onClick={onGenerate}>Generar Audio</BtnPrimary>
        )}
      </ActionRow>

      <Header>
        <ColLabel>Guion — {scenes.length} escenas</ColLabel>
        <ColLabel>
          {generated ? `Voz en off — ${audioFiles.length} pistas` : 'Voz en off — pendiente'}
        </ColLabel>
      </Header>

      <SceneList>
        {scenes.map((s, i) => {
          const isMixing = mixingScene === s.scene_number
          const version = audioVersions[s.scene_number] ? `?v=${audioVersions[s.scene_number]}` : ''
          const sceneFileName = `scene_${String(s.scene_number).padStart(4, '0')}.wav`
          const audioFile = audioFiles.includes(sceneFileName) ? sceneFileName : audioFiles[i]

          return (
            <SceneCard key={s.scene_number}>
              {/* Narration row */}
              <NarrationRow>
                <SceneNum>#{s.scene_number}</SceneNum>
                <NarrationText>{s.narration}</NarrationText>
              </NarrationRow>

              {/* Audio player + SFX controls */}
              <ControlsRow>
                <AudioWrapper>
                  {isMixing && (
                    <AudioLoadingBadge>
                      <Spinner />
                      Mezclando SFX...
                    </AudioLoadingBadge>
                  )}
                  {generated && audioFile ? (
                    <AudioEl
                      key={`${audioFile}${version}`}
                      src={`${base}/audios/${audioFile}${version}`}
                      controls
                      preload="none"
                    />
                  ) : (
                    <PendingBar>▷ — sin generar</PendingBar>
                  )}
                </AudioWrapper>

                {generated && Object.keys(catalog).length > 0 && (
                  <SfxControl
                    scene={s}
                    catalog={catalog}
                    apiBase={apiBase}
                    ideaBase={base}
                    isMixing={isMixing}
                    onRerollStart={handleRerollStart}
                    onRerollDone={handleRerollDone}
                  />
                )}
              </ControlsRow>
            </SceneCard>
          )
        })}
      </SceneList>
    </>
  )
}
