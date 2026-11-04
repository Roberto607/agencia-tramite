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
  { value: 'certificacion_nacimiento', label: 'Certificación de Nacimiento' },
  { value: 'certificacion_antecedentes_penales', label: 'Certificación de antecedentes penales' },
  { value: 'certificacion_matrimonio_divorcio_solteria', label: 'Certificación de matrimonio, divorcio, Fe de soltería' },
  { value: 'certificacion_viudez', label: 'Certificación de viudez' },
  { value: 'certificacion_defuncion', label: 'Certificación de defunción' },
  { value: 'titulos_estudio_certificacion_notas_plan_tematico', label: 'Títulos de estudio, certificación de notas y plan temático' },
  { value: 'representacion_juridica', label: 'Representación jurídica (abogados)' },
  { value: 'traducciones_certificadas', label: 'Traducciones certificadas' },
  { value: 'apostillamiento_consulado', label: 'Apostillamiento Consulado' },
  { value: 'asesoramiento_empresarial', label: 'Asesoramiento empresarial: Pymes, TCP, CNA y otros actores económicos' },
  { value: 'otros', label: 'Otros' },
]

function Hero({ onStart }) {
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
          <button className="primary-button hero__action" onClick={onStart} type="button">
            Regístrate o inicia sesión <ArrowRight size={18} aria-hidden="true" />
          </button>
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

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function ApplicationForm({ sectionRef, onClose }) {
  const [step, setStep] = useState('register')
  const [authMode, setAuthMode] = useState('register')
  const [loginCredentials, setLoginCredentials] = useState({ email: '', password: '' })
  const [profile, setProfile] = useState({
    first_names: '',
    last_names: '',
    identification_type: '',
    identification_number: '',
    phone: '',
    email: '',
    password: '',
  })
  const [authToken, setAuthToken] = useState('')
  const [selectedServices, setSelectedServices] = useState([])
  const [serviceDocuments, setServiceDocuments] = useState({})
  const [applicationId, setApplicationId] = useState(null)
  const [submissionError, setSubmissionError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const fileInputRefs = useRef({})

  function addServiceDocuments(service, event) {
    const selectedFiles = Array.from(event.currentTarget.files ?? [])
    setServiceDocuments((current) => ({
      ...current,
      [service]: [
        ...(current[service] ?? []),
        ...selectedFiles.map((file) => ({ id: crypto.randomUUID(), file })),
      ],
    }))
    event.currentTarget.value = ''
    setSubmissionError('')
  }

  function removeServiceDocument(service, id) {
    setServiceDocuments((current) => ({
      ...current,
      [service]: (current[service] ?? []).filter((document) => document.id !== id),
    }))
  }

  async function getApiResult(response) {
    const result = await response.json()
    if (!response.ok) {
      const detail = result.detail || Object.entries(result)
        .flatMap(([field, messages]) => {
          const errors = Array.isArray(messages) ? messages : [messages]
          return errors.map((message) => `${field}: ${message}`)
        })
        .join(' ')
      throw new Error(detail || `No se pudo completar la operación (${response.status}).`)
    }
    return result
  }

  async function handleRegistration(event) {
    event.preventDefault()
    setSubmissionError('')
    setIsSubmitting(true)

    try {
      const result = await getApiResult(await fetch(`${API_BASE_URL}/api/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      }))
      setAuthToken(result.token)
      setProfile((current) => ({ ...current, password: '' }))
      setStep('services')
    } catch (error) {
      setSubmissionError(error instanceof Error ? error.message : 'No se pudo crear tu cuenta.')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleLogin(event) {
    event.preventDefault()
    setSubmissionError('')
    setIsSubmitting(true)

    try {
      const result = await getApiResult(await fetch(`${API_BASE_URL}/api/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginCredentials),
      }))
      setAuthToken(result.token)
      setProfile({ ...result.profile, password: '' })
      setStep('services')
    } catch (error) {
      setSubmissionError(error instanceof Error ? error.message : 'No se pudo iniciar sesión.')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleApplicationSubmit(event) {
    event.preventDefault()
    if (selectedServices.length === 0) {
      setSubmissionError('Selecciona al menos un trámite.')
      return
    }

    const formElement = event.currentTarget
    const formData = new FormData(formElement)
    Object.entries(profile).forEach(([field, value]) => {
      if (field !== 'password') formData.set(field, value)
    })
    formData.set('selected_services', JSON.stringify(selectedServices))
    selectedServices.forEach((service) => {
      const documents = serviceDocuments[service] ?? []
      documents.forEach(({ file }) => {
        formData.append(`documents_${service}`, file)
      })
    })
    setSubmissionError('')
    setIsSubmitting(true)

    try {
      const result = await getApiResult(await fetch(`${API_BASE_URL}/api/applications/`, {
        method: 'POST',
        headers: { Authorization: `Token ${authToken}` },
        body: formData,
      }))
      setApplicationId(result.id)
      setStep('complete')
    } catch (error) {
      setSubmissionError(
        error instanceof TypeError
          ? 'No pudimos confirmar el resultado del envío. La solicitud podría haberse guardado; verifica con el equipo antes de volver a enviarla.'
          : error instanceof Error
            ? error.message
            : 'No se pudo conectar con el servidor.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="application-section" id="tramites" ref={sectionRef} aria-labelledby="application-title">
      <div className="application-inner">
        <div className="application-heading">
          <span className="application-eyebrow">Solicitud en línea</span>
          <h2 id="application-title">
            {step === 'register'
              ? authMode === 'register' ? 'Crea tu cuenta' : 'Inicia sesión'
              : step === 'services' ? 'Selecciona tus trámites' : 'Solicitud enviada'}
          </h2>
          <p>
            {step === 'register'
              ? authMode === 'register'
                ? 'Regístrate para continuar con tu consulta.'
                : 'Ingresa con el correo y la contraseña de tu cuenta.'
              : step === 'services'
                ? 'Elige uno o más trámites y adjunta sus documentos.'
                : 'Ya recibimos tu consulta.'}
          </p>
        </div>

        {step === 'register' && authMode === 'register' && (
          <form className="application-form" onSubmit={handleRegistration} aria-busy={isSubmitting}>
            <div className="form-grid">
              <label className="form-field">
                <span>Nombre(s) <span className="required-mark">*</span></span>
                <input autoComplete="given-name" name="first_names" onChange={(event) => setProfile({ ...profile, first_names: event.target.value })} placeholder="Escribe tu nombre" required value={profile.first_names} />
              </label>
              <label className="form-field">
                <span>Apellidos <span className="required-mark">*</span></span>
                <input autoComplete="family-name" name="last_names" onChange={(event) => setProfile({ ...profile, last_names: event.target.value })} placeholder="Escribe tus apellidos" required value={profile.last_names} />
              </label>
              <label className="form-field">
                <span>Tipo de identificación <span className="required-mark">*</span></span>
                <select name="identification_type" onChange={(event) => setProfile({ ...profile, identification_type: event.target.value })} required value={profile.identification_type}>
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
                <input autoComplete="off" name="identification_number" onChange={(event) => setProfile({ ...profile, identification_number: event.target.value })} placeholder="Número de documento" required value={profile.identification_number} />
              </label>
              <label className="form-field">
                <span>Teléfono <span className="required-mark">*</span></span>
                <input autoComplete="tel" name="phone" onChange={(event) => setProfile({ ...profile, phone: event.target.value })} placeholder="+53 58049659" required type="tel" value={profile.phone} />
              </label>
              <label className="form-field">
                <span>Correo electrónico <span className="required-mark">*</span></span>
                <input autoComplete="email" name="email" onChange={(event) => setProfile({ ...profile, email: event.target.value })} placeholder="nombre@correo.com" required type="email" value={profile.email} />
              </label>
              <label className="form-field form-field--full">
                <span>Contraseña <span className="required-mark">*</span></span>
                <input autoComplete="new-password" minLength="8" name="password" onChange={(event) => setProfile({ ...profile, password: event.target.value })} required type="password" value={profile.password} />
                <span className="field-hint">Usa al menos 8 caracteres y evita contraseñas comunes.</span>
              </label>
            </div>
            <div className="form-actions">
              <p><span className="required-mark">*</span> Campos obligatorios</p>
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? 'Creando cuenta...' : 'Registrarme y continuar'} <ArrowRight size={18} aria-hidden="true" />
              </button>
            </div>
            <p className="auth-switch">
              ¿Ya tienes cuenta?{' '}
              <button onClick={() => { setAuthMode('login'); setSubmissionError('') }} type="button">Inicia sesión</button>
            </p>
            {submissionError && <p className="form-notice form-notice--error" role="alert">{submissionError}</p>}
          </form>
        )}

        {step === 'register' && authMode === 'login' && (
          <form className="application-form" onSubmit={handleLogin} aria-busy={isSubmitting}>
            <div className="form-grid">
              <label className="form-field form-field--full">
                <span>Correo electrónico <span className="required-mark">*</span></span>
                <input
                  autoComplete="email"
                  onChange={(event) => setLoginCredentials({ ...loginCredentials, email: event.target.value })}
                  required
                  type="email"
                  value={loginCredentials.email}
                />
              </label>
              <label className="form-field form-field--full">
                <span>Contraseña <span className="required-mark">*</span></span>
                <input
                  autoComplete="current-password"
                  onChange={(event) => setLoginCredentials({ ...loginCredentials, password: event.target.value })}
                  required
                  type="password"
                  value={loginCredentials.password}
                />
              </label>
            </div>
            <div className="form-actions">
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? 'Iniciando sesión...' : 'Iniciar sesión y continuar'} <ArrowRight size={18} aria-hidden="true" />
              </button>
            </div>
            <p className="auth-switch">
              ¿No tienes cuenta?{' '}
              <button onClick={() => { setAuthMode('register'); setSubmissionError('') }} type="button">Regístrate</button>
            </p>
            {submissionError && <p className="form-notice form-notice--error" role="alert">{submissionError}</p>}
          </form>
        )}

        {step === 'services' && (
          <form className="application-form" onSubmit={handleApplicationSubmit} aria-busy={isSubmitting}>
            <div className="form-grid">
              <fieldset className="form-field form-field--full service-selection">
                <legend>Selecciona los trámites que necesitas <span className="required-mark">*</span></legend>
                <p className="service-selection__hint">Puedes marcar más de uno.</p>
                <div className="service-selection__options">
                  {serviceCatalog.map(({ value, label }) => (
                    <label className="service-option" key={value}>
                      <input
                        checked={selectedServices.includes(value)}
                        name="service_options"
                        onChange={(event) => {
                          setSelectedServices((current) => event.target.checked
                            ? [...current, value]
                            : current.filter((service) => service !== value))
                          setSubmissionError('')
                        }}
                        type="checkbox"
                        value={value}
                      />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              {selectedServices.includes('otros') && (
                <label className="form-field form-field--full">
                  <span>Describe tu trámite <span className="required-mark">*</span></span>
                  <textarea
                    name="other_service"
                    placeholder="Escribe el trámite que necesitas."
                    rows="4"
                    required
                  />
                </label>
              )}

              {selectedServices.map((service) => {
                const label = serviceCatalog.find((item) => item.value === service)?.label ?? service
                const documents = serviceDocuments[service] ?? []
                return (
                  <div className="form-field form-field--full service-documents" key={service}>
                    <span>Documentos para: {label} <span className="field-hint">Opcional</span></span>
                    <input
                      accept="image/*,.pdf,.doc,.docx"
                      className="visually-hidden"
                      multiple
                      onChange={(event) => addServiceDocuments(service, event)}
                      ref={(element) => { fileInputRefs.current[service] = element }}
                      type="file"
                    />
                    <div className="documents-upload">
                      <div className="documents-upload__intro">
                        <div className="documents-upload__icon"><FilePlus2 size={21} aria-hidden="true" /></div>
                        <div className="upload-copy">
                          <strong>Adjunta fotos o documentos</strong>
                          <span>Puedes seleccionar varios archivos para este trámite.</span>
                        </div>
                        <button className="secondary-button" onClick={() => fileInputRefs.current[service]?.click()} type="button">
                          <ImagePlus size={16} aria-hidden="true" /> Agregar archivos
                        </button>
                      </div>
                      {documents.length > 0 && (
                        <ul className="document-list" aria-label={`Archivos para ${label}`}>
                          {documents.map(({ id, file }) => (
                            <li className="document-item" key={id}>
                              <FileText size={18} aria-hidden="true" />
                              <span className="document-item__name">{file.name}</span>
                              <span className="document-item__size">{formatFileSize(file.size)}</span>
                              <button
                                aria-label={`Quitar ${file.name}`}
                                className="remove-file-button"
                                onClick={() => removeServiceDocument(service, id)}
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
                )
              })}
            </div>

            <div className="form-actions">
              <p><span className="required-mark">*</span> Selecciona al menos un trámite.</p>
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? 'Enviando...' : 'Enviar solicitud'} <ArrowRight size={18} aria-hidden="true" />
              </button>
            </div>
            {submissionError && <p className="form-notice form-notice--error" role="alert">{submissionError}</p>}
          </form>
        )}

        {step === 'complete' && (
          <div className="application-form application-complete" role="status">
            <CheckCircle2 size={35} aria-hidden="true" />
            <div>
              <h3>Tu consulta #{applicationId} será analizada en un plazo de 72 horas.</h3>
              <p>Si necesitas ayuda, puedes contactarnos por WhatsApp.</p>
              <a className="phone-contact__link" href="https://wa.me/5358049659" target="_blank" rel="noreferrer">
                <MessageCircle size={17} aria-hidden="true" /> WhatsApp: +53 58049659
              </a>
            </div>
          </div>
        )}
        {step === 'register' && (
          <button className="application-close" onClick={onClose} type="button">Cerrar</button>
        )}
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
  const [applicationOpen, setApplicationOpen] = useState(false)
  const applicationRef = useRef(null)

  useEffect(() => {
    if (applicationOpen) {
      applicationRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [applicationOpen])

  return (
    <>
      <main>
        <Hero onStart={() => setApplicationOpen(true)} />
        <Benefits />
        {applicationOpen && (
          <ApplicationForm
            onClose={() => setApplicationOpen(false)}
            sectionRef={applicationRef}
          />
        )}
        <PhoneContact />
        <section className="anchor-target" id="preguntas" aria-label="Preguntas frecuentes" />
      </main>
      <Footer />
    </>
  )
}
