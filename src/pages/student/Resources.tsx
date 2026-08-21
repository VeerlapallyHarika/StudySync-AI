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
  'Study Notes': 'bg-cyan-400/15 text-cyan-100 border-cyan-300/20',
  Documents: 'bg-violet-400/15 text-violet-100 border-violet-300/20',
  'Useful Links': 'bg-emerald-400/15 text-emerald-100 border-emerald-300/20',
  Videos: 'bg-rose-400/15 text-rose-100 border-rose-300/20',
  Assignments: 'bg-amber-400/15 text-amber-100 border-amber-300/20',
  Other: 'bg-white/10 text-white border-white/15',
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
    'w-full liquid-glass rounded-2xl px-4 py-3 bg-transparent text-white placeholder:text-white/40 text-sm outline-none'
  const labelClass = 'block text-white/55 text-xs uppercase tracking-wide mb-2'

  return (
    <StudentLayout>
      <section className="px-6 py-14 md:py-20">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex justify-between items-center gap-4 flex-wrap">
            <Link
              to="/student/dashboard"
              className="liquid-glass rounded-full px-5 py-2 text-white/80 hover:text-white text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Dashboard
            </Link>
          </div>

          <div className="max-w-3xl">
            <h1
              className="text-4xl md:text-5xl text-white tracking-tight"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Resources
            </h1>
            <p className="text-white/55 text-sm mt-2">Share and discover study material with your group.</p>
          </div>

          <GlassCard className="p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6 text-white">
              <Upload size={18} className="text-cyan-400" />
              <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                Share a Resource
              </h2>
            </div>

            {notice ? (
              <div className="liquid-glass rounded-2xl border border-emerald-400/25 px-4 py-3 text-xs text-emerald-100 mb-5">
                {notice}
              </div>
            ) : null}
            {error ? (
              <div className="liquid-glass rounded-2xl border border-rose-400/25 px-4 py-3 text-xs text-rose-100 mb-5">
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
                    <option key={type} value={type} className="bg-black">
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
                  className={`${inputClass} file:mr-3 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-xs file:font-medium file:text-black`}
                />
              </div>
              <div className="md:col-span-2">
                <button
                  type="submit"
                  disabled={sharing}
                  className="rounded-full px-6 py-3 bg-white text-black text-sm font-medium flex items-center gap-2 transition-colors hover:bg-white/90 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Plus size={16} />
                  {sharing ? 'Sharing...' : 'Share Resource'}
                </button>
              </div>
            </form>
          </GlassCard>

          <div>
            <div className="flex items-center gap-3 mb-5 text-white">
              <FolderOpen size={18} className="text-violet-400" />
              <h2 className="text-2xl" style={{ fontFamily: "'Instrument Serif', serif" }}>
                Shared Resources
              </h2>
            </div>

            {error && resources.length === 0 ? (
              <GlassCard className="p-8 text-center text-rose-100 border border-rose-400/25 bg-rose-500/10">
                {error}
              </GlassCard>
            ) : loading ? (
              <GlassCard className="p-8 text-center text-white/70">Loading resources...</GlassCard>
            ) : resources.length === 0 ? (
              <GlassCard className="py-16 text-center">
                <FolderOpen size={36} className="mx-auto text-white/30 mb-4" />
                <p className="text-white/55 text-sm">No resources shared yet.</p>
              </GlassCard>
            ) : (
              <div className="space-y-3">
                {resources.map((resource) => (
                  <GlassCard key={resource.id} className="p-5 flex items-center gap-4">
                    <div className="w-11 h-11 rounded-xl liquid-glass flex items-center justify-center text-white flex-shrink-0">
                      {resource.url ? <Link2 size={18} /> : <FileText size={18} />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-white text-sm font-medium truncate">{resource.title}</p>
                      <p className="text-white/45 text-xs mt-0.5 truncate">
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
                        className="rounded-full w-10 h-10 liquid-glass text-white/70 hover:text-white flex items-center justify-center flex-shrink-0 transition-colors"
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
