import {
  ArrowRight,
  Check,
  CheckCircle2,
  Facebook,
  FilePlus2,
  FileText,
  Headset,
  ImagePlus,
  Instagram,
  LaptopMinimal,
  Mail,
  MessageCircle,
  MapPin,
  PhoneCall,
  Linkedin,
  ShieldCheck,
  Trash2,
  Zap,
  Youtube,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const benefits = [
  {
    title: 'Proceso rápido',
    description: 'Completa tus trámites en menos tiempo.',
    Icon: Zap,
  },
  {
    title: 'Seguro y confiable',
    description: 'Tus datos siempre protegidos.',
    Icon: ShieldCheck,
  },
  {
    title: '100% en línea',
    description: 'Desde cualquier lugar.',
    Icon: LaptopMinimal,
  },
  {
    title: 'Soporte especializado',
    description: 'Estamos para ayudarte.',
    Icon: Headset,
  },
]

const serviceCatalog = [
  'certificacion_nacimiento',
  'certificacion_antecedentes_penales',
  'certificacion_matrimonio_divorcio_solteria',
  'certificacion_viudez',
  'certificacion_defuncion',
  'titulos_estudio_certificacion_notas_plan_tematico',
  'representacion_juridica',
  'otros',
  'traducciones_certificadas',
  'apostillamiento_consulado',
]

const serviceLabels = {
  certificacion_nacimiento: 'Certificación de Nacimiento',
  certificacion_antecedentes_penales: 'Certificación de antecedentes penales',
  certificacion_matrimonio_divorcio_solteria: 'Certificación de matrimonio, divorcio, Fe de soltería',
  certificacion_viudez: 'Certificación de viudez',
  certificacion_defuncion: 'Certificación de defunción',
  titulos_estudio_certificacion_notas_plan_tematico: 'Títulos de estudio, certificación de notas y plan temático',
  representacion_juridica: 'Representación jurídica (abogados)',
  otros: 'Otros',
  traducciones_certificadas: 'Traducciones certificadas',
  apostillamiento_consulado: 'Apostillamiento Consulado',
}

function Hero() {
  return (
    <section className="hero" id="inicio" aria-labelledby="hero-title">
      <div className="hero__image" aria-hidden="true" />
      <div className="hero__content">
        <div className="hero__copy">
          <div className="hero__badge">
            <span className="hero__badge-icon"><Check size={16} strokeWidth={3} /></span>
            Tu gestión, más fácil y rápido
          </div>
          <h1 id="hero-title">LB&amp;A Consulter<br /><span>Agencia de trámites y consultoría</span></h1>
          <p>Realiza tus trámites de forma ágil, segura y 100% en línea.<br className="desktop-break" /> Ahorra tiempo y evita filas.</p>
        </div>
      </div>
    </section>
  )
}

function Benefits() {
  return (
    <section className="benefits" id="servicios" aria-label="Beneficios">
      <div className="benefits-inner">
        {benefits.map(({ title, description, Icon }) => (
          <article className="benefit" key={title}>
            <div className="benefit__icon"><Icon size={34} strokeWidth={2.4} aria-hidden="true" /></div>
            <div className="benefit__copy">
              <h2>{title}</h2>
              <p>{description}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function ServiceCatalog() {
  return (
    <section className="service-catalog" aria-labelledby="service-catalog-title">
      <div className="service-catalog__header">
        <span className="application-eyebrow">Trámites que realizamos</span>
        <h2 id="service-catalog-title">Servicios de consultoría y gestión</h2>
      </div>
      <div className="service-catalog__grid">
        {serviceCatalog.map((value) => (
          <article className="service-item" key={value}>
            <span className="service-item__tag">Trámite</span>
            <h3>{serviceLabels[value]}</h3>
          </article>
        ))}
      </div>
    </section>
  )
}

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function ApplicationForm() {
  const photoInput = useRef(null)
  const documentsInput = useRef(null)
  const [photo, setPhoto] = useState(null)
  const [photoUrl, setPhotoUrl] = useState('')
  const [documents, setDocuments] = useState([])
  const [selectedService, setSelectedService] = useState('')
  const [notice, setNotice] = useState('')
  const [submissionError, setSubmissionError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!photo) {
      setPhotoUrl('')
      return undefined
    }

    const url = URL.createObjectURL(photo)
    setPhotoUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [photo])

  function addDocuments(event) {
    const selectedFiles = Array.from(event.currentTarget.files ?? [])
    setDocuments((current) => [
      ...current,
      ...selectedFiles.map((file) => ({ id: crypto.randomUUID(), file })),
    ])
    event.currentTarget.value = ''
    setNotice('')
    setSubmissionError('')
  }

  function removeDocument(id) {
    setDocuments((current) => current.filter((document) => document.id !== id))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const formElement = event.currentTarget
    const formData = new FormData(formElement)
    documents.forEach(({ file }) => formData.append('documents', file))
    setNotice('')
    setSubmissionError('')
    setIsSubmitting(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/`, {
        method: 'POST',
        body: formData,
      })
      const result = await response.json()

      if (!response.ok) {
        const detail = result.detail || Object.entries(result)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(' ') : messages}`)
          .join(' ')
        throw new Error(detail || `No se pudo enviar la solicitud (${response.status}).`)
      }

      setNotice(`Tu solicitud fue enviada correctamente y será revisada por nuestro equipo. Tu número de radicado es #${result.id}.`)
      formElement.reset()
      setPhoto(null)
      setDocuments([])
      setSelectedService('')
    } catch (error) {
      setSubmissionError(error instanceof Error ? error.message : 'No se pudo conectar con el servidor.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="application-section" id="tramites" aria-labelledby="application-title">
      <div className="application-inner">
        <div className="application-heading">
          <span className="application-eyebrow">Solicitud en línea</span>
          <h2 id="application-title">Inicia tu trámite</h2>
          <p>Completa tus datos y adjunta los documentos necesarios.</p>
        </div>

        <form className="application-form" onSubmit={handleSubmit} aria-busy={isSubmitting}>
          <div className="form-grid">
            <label className="form-field">
              <span>Nombre(s) <span className="required-mark">*</span></span>
              <input autoComplete="given-name" name="first_names" placeholder="Escribe tu nombre" required />
            </label>
            <label className="form-field">
              <span>Apellidos <span className="required-mark">*</span></span>
              <input autoComplete="family-name" name="last_names" placeholder="Escribe tus apellidos" required />
            </label>
            <label className="form-field">
              <span>Tipo de identificación <span className="required-mark">*</span></span>
              <select name="identification_type" defaultValue="" required>
                <option value="" disabled>Selecciona una opción</option>
                <option value="cedula">Cédula de ciudadanía</option>
                <option value="extranjeria">Cédula de extranjería</option>
                <option value="pasaporte">Pasaporte</option>
                <option value="nit">NIT</option>
                <option value="otro">Otro</option>
              </select>
            </label>
            <label className="form-field">
              <span>Número de identificación <span className="required-mark">*</span></span>
              <input autoComplete="off" inputMode="numeric" name="identification_number" placeholder="Número de documento" required />
            </label>
            <label className="form-field">
              <span>Correo electrónico <span className="required-mark">*</span></span>
              <input autoComplete="email" name="email" type="email" placeholder="nombre@correo.com" required />
            </label>
            <label className="form-field">
              <span>Teléfono</span>
              <input autoComplete="tel" name="phone" type="tel" placeholder="+57 300 000 0000" />
            </label>

            <label className="form-field form-field--full">
              <span>Tipo de trámite <span className="required-mark">*</span></span>
              <select name="service_type" onChange={(event) => setSelectedService(event.target.value)} value={selectedService} required>
                <option value="" disabled>Selecciona el trámite que necesitas</option>
                <option value="certificacion_nacimiento">Certificación de Nacimiento</option>
                <option value="certificacion_antecedentes_penales">Certificación de antecedentes penales</option>
                <option value="certificacion_matrimonio_divorcio_solteria">Certificación de matrimonio, divorcio, Fe de soltería</option>
                <option value="certificacion_viudez">Certificación de viudez</option>
                <option value="certificacion_defuncion">Certificación de defunción</option>
                <option value="titulos_estudio_certificacion_notas_plan_tematico">Títulos de estudio, certificación de notas y plan temático</option>
                <option value="representacion_juridica">Representación jurídica (abogados)</option>
                <option value="otros">Otros</option>
                <option value="traducciones_certificadas">Traducciones certificadas</option>
                <option value="apostillamiento_consulado">Apostillamiento Consulado</option>
              </select>
            </label>

            {selectedService === 'otros' && (
              <label className="form-field form-field--full">
                <span>Describe tu trámite <span className="required-mark">*</span></span>
                <textarea
                  name="other_service"
                  placeholder="Escribe el trámite que necesitas, por ejemplo: apostillamiento de título, trámite notarial, etc."
                  rows="4"
                  required
                />
              </label>
            )}

            <div className="form-field form-field--full">
              <span>Foto <span className="field-hint">Opcional</span></span>
              <div className="photo-upload">
                <input
                  accept="image/*"
                  className="visually-hidden"
                  name="photo"
                  onChange={(event) => setPhoto(event.currentTarget.files?.[0] ?? null)}
                  ref={photoInput}
                  type="file"
                />
                {photoUrl ? (
                  <img className="photo-preview" src={photoUrl} alt="Vista previa de la foto seleccionada" />
                ) : (
                  <div className="photo-placeholder"><ImagePlus size={25} aria-hidden="true" /></div>
                )}
                <div className="upload-copy">
                  <strong>{photo?.name ?? 'Agrega una foto de identificación'}</strong>
                  <span>Imagen JPG, PNG o similar</span>
                </div>
                <button className="secondary-button" onClick={() => photoInput.current?.click()} type="button">
                  {photo ? 'Cambiar foto' : 'Seleccionar foto'}
                </button>
              </div>
            </div>

            <div className="form-field form-field--full">
              <span>Documentos <span className="field-hint">Puedes agregar varios</span></span>
              <input className="visually-hidden" multiple onChange={addDocuments} ref={documentsInput} type="file" />
              <div className="documents-upload">
                <div className="documents-upload__intro">
                  <div className="documents-upload__icon"><FilePlus2 size={21} aria-hidden="true" /></div>
                  <div className="upload-copy">
                    <strong>Adjunta tus documentos</strong>
                    <span>Selecciona uno o varios archivos. Puedes añadir más después.</span>
                  </div>
                  <button className="secondary-button" onClick={() => documentsInput.current?.click()} type="button">
                    <ImagePlus size={16} aria-hidden="true" /> Agregar archivos
                  </button>
                </div>
                {documents.length > 0 && (
                  <ul className="document-list" aria-label="Documentos adjuntos">
                    {documents.map(({ id, file }) => (
                      <li className="document-item" key={id}>
                        <FileText size={18} aria-hidden="true" />
                        <span className="document-item__name">{file.name}</span>
                        <span className="document-item__size">{formatFileSize(file.size)}</span>
                        <button
                          aria-label={`Quitar ${file.name}`}
                          className="remove-file-button"
                          onClick={() => removeDocument(id)}
                          type="button"
                        >
                          <Trash2 size={17} aria-hidden="true" />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>

          <div className="form-actions">
            <p><span className="required-mark">*</span> Campos obligatorios</p>
            <button className="primary-button" disabled={isSubmitting} type="submit">
              {isSubmitting ? 'Enviando...' : 'Enviar solicitud'} <ArrowRight size={18} aria-hidden="true" />
            </button>
          </div>
          {notice && (
            <p className="form-notice" role="status">
              <CheckCircle2 size={19} aria-hidden="true" /> {notice}
            </p>
          )}
          {submissionError && <p className="form-notice form-notice--error" role="alert">{submissionError}</p>}
        </form>
      </div>
    </section>
  )
}

function PhoneContact() {
  return (
    <section className="phone-contact" aria-labelledby="phone-contact-title">
      <div className="phone-contact__inner">
        <div className="phone-contact__icon"><PhoneCall size={25} aria-hidden="true" /></div>
        <div className="phone-contact__copy">
          <h2 id="phone-contact-title">¿Necesitas ayuda con tu trámite?</h2>
          <p>Comunícate con nuestro equipo de atención.</p>
        </div>
        <a className="phone-contact__link" href="https://wa.me/5358049659" target="_blank" rel="noreferrer">
          <MessageCircle size={17} aria-hidden="true" /> WhatsApp: +53 58049659
        </a>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="site-footer" id="contacto">
      <div className="footer-main">
        <div className="footer-intro">
          <span className="footer-intro__eyebrow">LB&amp;A Consulter</span>
          <h2>Agencia de trámites<br />y consultoría</h2>
          <p>Atención y acompañamiento para tus gestiones.</p>
        </div>
        <div className="footer-contact">
          <h2>Contacto</h2>
          <a href="https://wa.me/5358049659" target="_blank" rel="noreferrer"><MessageCircle size={17} aria-hidden="true" /> +53 58049659</a>
          <a href="mailto:lbaconsulter@gmail.com"><Mail size={17} fill="currentColor" aria-hidden="true" /> lbaconsulter@gmail.com</a>
          <p><MapPin size={18} fill="currentColor" aria-hidden="true" /> Cra. 123 #45-67, Ciudad</p>
        </div>
        <div className="footer-social">
          <h2>Síguenos</h2>
          <div className="social-links">
            <a href="https://www.facebook.com/" aria-label="Facebook" title="Facebook"><Facebook size={18} aria-hidden="true" /></a>
            <a href="https://www.instagram.com/" aria-label="Instagram" title="Instagram"><Instagram size={18} aria-hidden="true" /></a>
            <a href="https://www.youtube.com/" aria-label="YouTube" title="YouTube"><Youtube size={18} aria-hidden="true" /></a>
            <a href="https://www.linkedin.com/" aria-label="LinkedIn" title="LinkedIn"><Linkedin size={18} aria-hidden="true" /></a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} LB&amp;A Consulter. Todos los derechos reservados.</span>
        <span>Agencia de trámites y consultoría</span>
      </div>
    </footer>
  )
}

export default function App() {
  return (
    <>
      <main>
        <Hero />
        <Benefits />
        <ServiceCatalog />
        <ApplicationForm />
        <PhoneContact />
        <section className="anchor-target" id="preguntas" aria-label="Preguntas frecuentes" />
      </main>
      <Footer />
    </>
  )
}
