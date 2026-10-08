import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, FileText, FolderOpen, Link2, Plus, Upload } from 'lucide-react'
import GlassCard from '../../components/GlassCard'
import StudentLayout from '../../layouts/StudentLayout'
import usePageTitle from '../../hooks/usePageTitle'
import { getStudentResources, shareGroupResource } from '../../services/studentService'
import type { ResourceType, SharedResourceItem } from '../../types/student'

const RESOURCE_TYPES: ResourceType[] = ['Study Notes', 'Documents', 'Useful Links', 'Videos', 'Assignments', 'Other']

const typeStyles: Record<ResourceType, string> = {
  'Study Notes': 'bg-mauve/35 text-ivory border-mauve/70',
  Documents: 'bg-plum/85 text-ivory/95 border-mauve/50',
  'Useful Links': 'bg-ivory/10 text-ivory border-ivory/30',
  Videos: 'bg-blush/15 text-blush border-blush/40',
  Assignments: 'bg-mauve/15 text-blush border-mauve/70',
  Other: 'bg-ivory/5 text-ivory/70 border-plum',
}

export default function StudentResourcesPage() {
  usePageTitle('Resources')
  const [resources, setResources] = useState<SharedResourceItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const [title, setTitle] = useState('')
  const [resourceType, setResourceType] = useState<ResourceType>('Study Notes')
  const [url, setUrl] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [sharing, setSharing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setResources(await getStudentResources())
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load resources.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleShare = async (event: FormEvent) => {
    event.preventDefault()
    if (!title.trim()) {
      setError('Please provide a title for the resource.')
      return
    }
    if (!url.trim() && !file) {
      setError('Add either a URL or attach a file to share.')
      return
    }

    setSharing(true)
    setError('')
    setNotice('')
    try {
      const shared = await shareGroupResource({ title: title.trim(), resourceType, url: url.trim() || undefined, file })
      setResources((current) => [shared, ...current])
      setTitle('')
      setUrl('')
      setFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setNotice('Resource shared with your group.')
      window.setTimeout(() => setNotice(''), 3000)
    } catch (shareError) {
      setError(shareError instanceof Error ? shareError.message : 'Unable to share the resource.')
    } finally {
      setSharing(false)
    }
  }

  const inputClass =
    'w-full liquid-glass rounded-2xl px-4 py-3 bg-transparent text-ivory placeholder:text-ivory/40 text-sm outline-none'
  const labelClass = 'block text-ivory/55 text-xs uppercase tracking-wide mb-2'

  return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex justify-between items-center gap-4 flex-wrap">
            <Link
              to="/student/dashboard"
              className="liquid-glass rounded-full px-5 py-2 text-ivory/80 hover:text-ivory text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>
          </div>

          <div className="max-w-3xl">
            <h1
              className="text-4xl md:text-5xl text-ivory tracking-tight"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Resources
            </h1>
            <p className="text-ivory/55 text-sm mt-2">Share and discover study material with your group.</p>
          </div>

          <GlassCard className="p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6 text-ivory">
              <Upload size={18} className="text-blush" />
              <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                Share a Resource
              </h2>
            </div>

            {notice ? (
              <div className="liquid-glass rounded-2xl border border-ivory/30 px-4 py-3 text-xs text-ivory mb-5">
                {notice}
              </div>
            ) : null}
            {error ? (
              <div className="liquid-glass rounded-2xl border border-blush/35 px-4 py-3 text-xs text-blush mb-5">
                {error}
              </div>
            ) : null}

            <form onSubmit={handleShare} className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className={labelClass} htmlFor="resourceTitle">Title</label>
                <input
                  id="resourceTitle"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="e.g. Calculus cheat sheet"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass} htmlFor="resourceType">Type</label>
                <select
                  id="resourceType"
                  value={resourceType}
                  onChange={(event) => setResourceType(event.target.value as ResourceType)}
                  className={inputClass}
                >
                  {RESOURCE_TYPES.map((type) => (
                    <option key={type} value={type} className="bg-ink">
                      {type}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className={labelClass} htmlFor="resourceUrl">URL (optional)</label>
                <input
                  id="resourceUrl"
                  type="url"
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  placeholder="https://..."
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass} htmlFor="resourceFile">File (optional)</label>
                <input
                  id="resourceFile"
                  ref={fileInputRef}
                  type="file"
                  onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                  className={`${inputClass} file:mr-3 file:rounded-full file:border-0 file:bg-blush file:px-4 file:py-2 file:text-xs file:font-medium file:text-ink`}
                />
              </div>
              <div className="md:col-span-2">
                <button
                  type="submit"
                  disabled={sharing}
                  className="rounded-full px-6 py-3 bg-blush text-ink text-sm font-medium flex items-center gap-2 transition-colors hover:bg-blush/90 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Plus size={16} />
                  {sharing ? 'Sharing...' : 'Share Resource'}
                </button>
              </div>
            </form>
          </GlassCard>

          <div>
            <div className="flex items-center gap-3 mb-5 text-ivory">
              <FolderOpen size={18} className="text-blush" />
              <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                Shared Resources
              </h2>
            </div>

            {error && resources.length === 0 ? (
              <GlassCard className="p-8 text-center text-blush border border-blush/35 bg-blush/12">
                {error}
              </GlassCard>
            ) : loading ? (
              <GlassCard className="p-8 text-center text-ivory/70">Loading resources...</GlassCard>
            ) : resources.length === 0 ? (
              <GlassCard className="py-16 text-center">
                <FolderOpen size={36} className="mx-auto text-ivory/30 mb-4" />
                <p className="text-ivory/55 text-sm">No resources shared yet.</p>
              </GlassCard>
            ) : (
              <div className="space-y-3">
                {resources.map((resource) => (
                  <GlassCard key={resource.id} className="p-5 flex items-center gap-4">
                    <div className="w-11 h-11 rounded-xl liquid-glass flex items-center justify-center text-ivory flex-shrink-0">
                      {resource.url ? <Link2 size={18} /> : <FileText size={18} />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-ivory text-sm font-medium truncate">{resource.title}</p>
                      <p className="text-ivory/45 text-xs mt-0.5 truncate">
                        {resource.fileName ?? resource.url} · shared by {resource.uploader} ·{' '}
                        {new Date(resource.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <span
                      className={`rounded-full border px-3 py-1 text-xs whitespace-nowrap ${typeStyles[resource.resourceType]}`}
                    >
                      {resource.resourceType}
                    </span>
                    {resource.url ? (
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noreferrer"
                        aria-label={`Open ${resource.title}`}
                        className="rounded-full w-10 h-10 liquid-glass text-ivory/70 hover:text-ivory flex items-center justify-center flex-shrink-0 transition-colors"
                      >
                        <ExternalLink size={16} />
                      </a>
                    ) : null}
                  </GlassCard>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </StudentLayout>
  )
}
