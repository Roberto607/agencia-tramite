import {
  ArrowRight,
  CheckCircle2,
  FilePlus2,
  FileText,
  Eye,
  EyeOff,
  ImagePlus,
  MessageCircle,
  Trash2,
} from 'lucide-react'
import { useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const serviceCatalog = [
  {
    value: 'certificacion_nacimiento',
    label: 'Certificación de Nacimiento',
    pricingGroups: [
      { id: 'obtencion', label: 'Obtención', options: [{ id: 'obtencion', label: 'Obtención', time: '1–5 días', price: 6000, currency: 'CUP' }] },
      { id: 'legalizacion', label: 'Legalización', options: [
        { id: 'express', label: 'Vía express', time: '15–20 días', price: 70, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–45 días', price: 15000, currency: 'CUP' },
      ] },
    ],
  },
  {
    value: 'certificacion_antecedentes_penales',
    label: 'Certificación de antecedentes penales',
    pricingGroups: [
      { id: 'legalizacion', label: 'Legalización (incluye obtención)', options: [
        { id: 'express', label: 'Vía express', time: '15–30 días', price: 80, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–45 días', price: 25000, currency: 'CUP' },
      ] },
    ],
  },
  {
    value: 'certificacion_matrimonio_divorcio_solteria',
    label: 'Certificación de matrimonio, divorcio, Fe de soltería',
    pricingGroups: [
      { id: 'obtencion', label: 'Obtención', options: [{ id: 'obtencion', label: 'Obtención', time: '1–5 días', price: 7000, currency: 'CUP' }] },
      { id: 'legalizacion', label: 'Legalización', options: [
        { id: 'express', label: 'Vía express', time: '15–20 días', price: 70, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–45 días', price: 15000, currency: 'CUP' },
      ] },
    ],
  },
  {
    value: 'certificacion_viudez',
    label: 'Certificación de viudez',
    pricingGroups: [
      { id: 'obtencion', label: 'Obtención', options: [{ id: 'obtencion', label: 'Obtención', time: '1–5 días', price: 6000, currency: 'CUP' }] },
      { id: 'legalizacion', label: 'Legalización', options: [
        { id: 'express', label: 'Vía express', time: '15–20 días', price: 70, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–45 días', price: 15000, currency: 'CUP' },
      ] },
    ],
  },
  {
    value: 'certificacion_defuncion',
    label: 'Certificación de defunción',
    pricingGroups: [
      { id: 'obtencion', label: 'Obtención', options: [{ id: 'obtencion', label: 'Obtención', time: '1–10 días', price: 8000, currency: 'CUP' }] },
      { id: 'legalizacion', label: 'Legalización', options: [
        { id: 'express', label: 'Vía express', time: '15–20 días', price: 70, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–45 días', price: 15000, currency: 'CUP' },
      ] },
    ],
  },
  {
    value: 'titulos_estudio_certificacion_notas_plan_tematico',
    label: 'Títulos de estudio, certificación de notas y plan temático',
    pricingGroups: [
      { id: 'preuniversitario', label: 'Legalización (título preuniversitario o certificación de notas)', options: [
        { id: 'express', label: 'Vía express', time: '1–10 días', price: 150, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–90 días', price: 20000, currency: 'CUP' },
      ] },
      { id: 'universitario', label: 'Legalización (título universitario o certificación de notas)', options: [
        { id: 'lenta', label: 'Vía lenta', time: '30–90 días', price: 25000, currency: 'CUP' },
      ] },
      { id: 'plan_tematico', label: 'Legalización (plan temático)', options: [
        { id: 'express', label: 'Vía express', time: '1–10 días', price: 250, currency: 'USD' },
        { id: 'lenta', label: 'Vía lenta', time: '30–90 días', price: 35000, currency: 'CUP' },
      ] },
    ],
  },
  { value: 'representacion_juridica', label: 'Representación jurídica (abogados)', note: 'Tiempo y costo se informan al revisar tu consulta.' },
  {
    value: 'traducciones_certificadas',
    label: 'Traducciones certificadas',
    pricingGroups: [
      { id: 'traduccion', label: 'Traducción certificada', options: [{ id: 'traduccion', label: 'Traducción certificada', time: '1–5 días', price: 30, currency: 'USD' }] },
    ],
  },
  { value: 'apostillamiento_consulado', label: 'Apostillamiento Consulado', note: 'El tiempo y el costo dependen del consulado. Te brindaremos los detalles al contactarnos.' },
  { value: 'asesoramiento_empresarial', label: 'Asesoramiento empresarial: Pymes, TCP, CNA y otros actores económicos', note: 'Tiempo y costo se informan al revisar tu consulta.' },
  { value: 'otros', label: 'Otros', note: 'Te confirmaremos el tiempo y el costo según el trámite que necesitas.' },
]

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatPrice(option) {
  if (option.price == null || !option.currency) return 'Precio a consultar'
  return `${new Intl.NumberFormat('es-CU').format(option.price)} ${option.currency}`
}

function ApplicationForm() {
  const [step, setStep] = useState('register')
  const [authMode, setAuthMode] = useState('register')
  const [loginCredentials, setLoginCredentials] = useState({ email: '', password: '' })
  const [showRegistrationPassword, setShowRegistrationPassword] = useState(false)
  const [showLoginPassword, setShowLoginPassword] = useState(false)
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
  const [selectedPricingOptions, setSelectedPricingOptions] = useState({})
  const [serviceDocuments, setServiceDocuments] = useState({})
  const [otherServiceDescription, setOtherServiceDescription] = useState('')
  const [submissionError, setSubmissionError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const fileInputRefs = useRef({})
  const selectedPricingDetails = serviceCatalog.flatMap((service) =>
    (service.pricingGroups ?? []).flatMap((group) => {
      const optionId = selectedPricingOptions[service.value]?.[group.id]
      const option = group.options.find((item) => item.id === optionId)
      return option ? [{
        service: service.value,
        service_label: service.label,
        group: group.label,
        option: option.label,
        time: option.time,
        price: option.price,
        currency: option.currency,
      }] : []
    }),
  )
  const totals = selectedPricingDetails.reduce((result, option) => {
    if (option.currency) result[option.currency] = (result[option.currency] ?? 0) + option.price
    return result
  }, {})
  const hasUnpricedSelection = selectedPricingDetails.some((option) => option.price == null)
  const hasCustomPricedServices = selectedServices.some((serviceValue) =>
    !serviceCatalog.find((service) => service.value === serviceValue)?.pricingGroups,
  )
  const formattedTotal = [
    totals.CUP ? `${new Intl.NumberFormat('es-CU').format(totals.CUP)} CUP` : '',
    totals.USD ? `${new Intl.NumberFormat('en-US').format(totals.USD)} USD` : '',
  ].filter(Boolean).join(' + ') || 'Pendiente de cotización'
  const whatsappMessage = [
    'Hola, quiero solicitar estos trámites:',
    `Nombre: ${[profile.first_names, profile.last_names].filter(Boolean).join(' ') || 'No indicado'}.`,
    '',
    'Trámites solicitados:',
    ...selectedServices.flatMap((serviceValue) => {
      const service = serviceCatalog.find((item) => item.value === serviceValue)
      const options = selectedPricingDetails.filter((item) => item.service === serviceValue)
      const details = options.length > 0
        ? options.map((option) =>
          `  - ${option.group}: ${option.option} | ${option.time} | ${formatPrice(option)}`,
        )
        : [`  - ${service?.note ?? 'Tiempo y costo por confirmar.'}`]
      if (serviceValue === 'otros' && otherServiceDescription.trim()) {
        details.push(`  - Detalle: ${otherServiceDescription.trim()}`)
      }
      return [`- ${service?.label ?? serviceValue}`, ...details]
    }),
    '',
    `Total estimado: ${formattedTotal}`,
    ...(hasUnpricedSelection || hasCustomPricedServices
      ? ['Hay conceptos cuyo precio debe confirmarse al revisar la solicitud.']
      : []),
  ].join('\n')

  function addServiceDocuments(service, fileType, event) {
    const selectedFiles = Array.from(event.currentTarget.files ?? [])
    setServiceDocuments((current) => ({
      ...current,
      [service]: [
        ...(current[service] ?? []),
        ...selectedFiles.map((file) => ({ id: crypto.randomUUID(), file, fileType })),
      ],
    }))
    if (!selectedServices.includes(service)) toggleService(service, true)
    event.currentTarget.value = ''
    setSubmissionError('')
  }

  function removeServiceDocument(service, id) {
    setServiceDocuments((current) => ({
      ...current,
      [service]: (current[service] ?? []).filter((document) => document.id !== id),
    }))
  }

  function toggleService(service, isSelected) {
    setSelectedServices((current) => isSelected
      ? [...current, service]
      : current.filter((selectedService) => selectedService !== service))
    if (isSelected) {
      const catalogEntry = serviceCatalog.find((item) => item.value === service)
      const defaults = Object.fromEntries(
        (catalogEntry?.pricingGroups ?? [])
          .filter((group) => group.options.length === 1)
          .map((group) => [group.id, group.options[0].id]),
      )
      setSelectedPricingOptions((current) => ({ ...current, [service]: defaults }))
    } else {
      setSelectedPricingOptions((current) => {
        const remainingOptions = { ...current }
        delete remainingOptions[service]
        return remainingOptions
      })
    }
    if (!isSelected) {
      setServiceDocuments((current) => {
        const remainingDocuments = { ...current }
        delete remainingDocuments[service]
        return remainingDocuments
      })
    }
    setSubmissionError('')
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
      setStep('registered')
    } catch (error) {
      setSubmissionError(error instanceof Error ? error.message : 'No se pudo crear la cuenta.')
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
    const serviceMissingOptions = selectedServices.find((serviceValue) => {
      const service = serviceCatalog.find((item) => item.value === serviceValue)
      return service?.pricingGroups?.length
        && !selectedPricingDetails.some((option) => option.service === serviceValue)
    })
    if (serviceMissingOptions) {
      const service = serviceCatalog.find((item) => item.value === serviceMissingOptions)
      setSubmissionError(`Selecciona al menos una opción para ${service?.label}.`)
      return
    }

    const formElement = event.currentTarget
    const formData = new FormData(formElement)
    Object.entries(profile).forEach(([field, value]) => {
      if (field !== 'password') formData.set(field, value)
    })
    formData.set('selected_services', JSON.stringify(selectedServices))
    formData.set('selected_options', JSON.stringify(selectedPricingDetails))
    selectedServices.forEach((service) => {
      const documents = serviceDocuments[service] ?? []
      documents.forEach(({ file, fileType }) => {
        const fieldPrefix = fileType === 'photo' ? 'photos' : 'documents'
        formData.append(`${fieldPrefix}_${service}`, file)
      })
    })
    setSubmissionError('')
    setIsSubmitting(true)

    try {
      let submissionToken = authToken
      if (!submissionToken) {
        const registration = await getApiResult(await fetch(`${API_BASE_URL}/api/register/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profile),
        }))
        submissionToken = registration.token
        setAuthToken(submissionToken)
        setProfile((current) => ({ ...current, password: '' }))
      }

      await getApiResult(await fetch(`${API_BASE_URL}/api/applications/`, {
        method: 'POST',
        headers: { Authorization: `Token ${submissionToken}` },
        body: formData,
      }))
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
    <section className="application-section" aria-labelledby="application-title">
      <div className="application-inner">
        <div className="application-heading">
          <span className="application-eyebrow">Solicitud en línea</span>
          <h2 id="application-title">
            {step === 'register'
              ? authMode === 'register' ? 'Crea tu cuenta' : 'Inicia sesión'
              : step === 'registered'
                ? 'Cuenta creada'
                : step === 'services' ? 'Selecciona tus trámites' : 'Trámites listos para enviar'}
          </h2>
          <p>
            {step === 'register'
              ? authMode === 'register'
                ? 'Completa tus datos para crear tu cuenta. Puedes seleccionar tus trámites ahora o hacerlo después.'
                : 'Ingresa con el correo y la contraseña de tu cuenta.'
              : step === 'registered'
                ? 'Tu cuenta ya está lista. Puedes elegir tus trámites ahora o iniciar sesión más adelante.'
                : step === 'services'
                  ? 'Elige uno o más trámites y adjunta sus documentos.'
                  : 'Tus datos y trámites quedaron guardados en la plataforma. Para contactar con nosotros, revisa y envía el mensaje por WhatsApp.'}
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
                <span className="password-input-wrap">
                  <input autoComplete="new-password" minLength="8" name="password" onChange={(event) => setProfile({ ...profile, password: event.target.value })} required type={showRegistrationPassword ? 'text' : 'password'} value={profile.password} />
                  <button
                    aria-label={showRegistrationPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                    aria-pressed={showRegistrationPassword}
                    className="password-visibility-toggle"
                    onClick={() => setShowRegistrationPassword((visible) => !visible)}
                    type="button"
                  >
                    {showRegistrationPassword
                      ? <EyeOff size={19} aria-hidden="true" />
                      : <Eye size={19} aria-hidden="true" />}
                  </button>
                </span>
                <span className="field-hint">Usa al menos 8 caracteres y evita contraseñas comunes.</span>
              </label>
            </div>
            <div className="form-actions">
              <p><span className="required-mark">*</span> Campos obligatorios</p>
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? 'Creando cuenta...' : 'Crear cuenta'} <ArrowRight size={18} aria-hidden="true" />
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
                <span className="password-input-wrap">
                  <input
                    autoComplete="current-password"
                    onChange={(event) => setLoginCredentials({ ...loginCredentials, password: event.target.value })}
                    required
                    type={showLoginPassword ? 'text' : 'password'}
                    value={loginCredentials.password}
                  />
                  <button
                    aria-label={showLoginPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                    aria-pressed={showLoginPassword}
                    className="password-visibility-toggle"
                    onClick={() => setShowLoginPassword((visible) => !visible)}
                    type="button"
                  >
                    {showLoginPassword
                      ? <EyeOff size={19} aria-hidden="true" />
                      : <Eye size={19} aria-hidden="true" />}
                  </button>
                </span>
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

        {step === 'registered' && (
          <div className="application-form account-created" role="status">
            <span className="account-created__icon"><CheckCircle2 size={30} aria-hidden="true" /></span>
            <div className="account-created__content">
              <span className="account-created__eyebrow">Registro completado</span>
              <h3>¡Tu cuenta se creó correctamente!</h3>
              <p>Puedes continuar con tu trámite ahora o cancelarlo y volver más adelante iniciando sesión con tu cuenta.</p>
              <div className="account-created__actions">
                <button className="primary-button" onClick={() => setStep('services')} type="button">
                  Continuar trámite <ArrowRight size={18} aria-hidden="true" />
                </button>
                <button
                  className="account-created__cancel"
                  onClick={() => {
                    setAuthToken('')
                    setLoginCredentials({ email: profile.email, password: '' })
                    setAuthMode('login')
                    setStep('register')
                    setSubmissionError('')
                  }}
                  type="button"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 'services' && (
          <form className="application-form" onSubmit={handleApplicationSubmit} aria-busy={isSubmitting}>
            <div className="form-grid">
              <fieldset className="form-field form-field--full service-selection">
                <legend>Selecciona los trámites que necesitas <span className="required-mark">*</span></legend>
                <p className="service-selection__hint">Puedes marcar más de uno.</p>
                <div className="service-selection__options">
                  {serviceCatalog.map(({ value, label, pricingGroups, note }) => {
                    const isSelected = selectedServices.includes(value)
                    const documents = serviceDocuments[value] ?? []
                    const photoInputKey = `${value}-photo`
                    const documentInputKey = `${value}-document`

                    return (
                      <div className={`service-option${isSelected ? ' service-option--selected' : ''}`} key={value}>
                        <div className="service-option__row">
                          <label className="service-option__choice">
                            <input
                              checked={isSelected}
                              name="service_options"
                              onChange={(event) => toggleService(value, event.target.checked)}
                              type="checkbox"
                              value={value}
                            />
                            <span>{label}</span>
                          </label>
                          <div className="service-option__uploads">
                            <input
                              accept="image/*"
                              aria-label={`Foto para ${label}`}
                              className="visually-hidden"
                              multiple
                              onChange={(event) => addServiceDocuments(value, 'photo', event)}
                              ref={(element) => { fileInputRefs.current[photoInputKey] = element }}
                              type="file"
                            />
                            <button
                              aria-label={`Añadir foto para ${label}`}
                              className="service-upload-button"
                              onClick={() => fileInputRefs.current[photoInputKey]?.click()}
                              title="Añadir foto"
                              type="button"
                            >
                              <ImagePlus size={17} aria-hidden="true" />
                            </button>
                            <input
                              accept=".pdf,.doc,.docx,.odt,.rtf,.txt"
                              aria-label={`Documento para ${label}`}
                              className="visually-hidden"
                              multiple
                              onChange={(event) => addServiceDocuments(value, 'document', event)}
                              ref={(element) => { fileInputRefs.current[documentInputKey] = element }}
                              type="file"
                            />
                            <button
                              aria-label={`Añadir documento para ${label}`}
                              className="service-upload-button"
                              onClick={() => fileInputRefs.current[documentInputKey]?.click()}
                              title="Añadir documento"
                              type="button"
                            >
                              <FilePlus2 size={17} aria-hidden="true" />
                            </button>
                          </div>
                        </div>
                        {isSelected && pricingGroups && (
                          <div className="service-option__pricing">
                            {pricingGroups.map((group) => (
                              <label className="service-option__price-field" key={group.id}>
                                <span>{group.label}</span>
                                <select
                                  onChange={(event) => setSelectedPricingOptions((current) => ({
                                    ...current,
                                    [value]: { ...current[value], [group.id]: event.target.value },
                                  }))}
                                  value={selectedPricingOptions[value]?.[group.id] ?? ''}
                                >
                                  <option value="">No incluir</option>
                                  {group.options.map((option) => (
                                    <option key={option.id} value={option.id}>
                                      {option.label} · {option.time} · {formatPrice(option)}
                                    </option>
                                  ))}
                                </select>
                              </label>
                            ))}
                          </div>
                        )}
                        {isSelected && note && <p className="service-option__note">{note}</p>}
                        {documents.length > 0 && (
                          <ul className="service-option__files" aria-label={`Archivos para ${label}`}>
                            {documents.map(({ id, file, fileType }) => (
                              <li className="document-item" key={id}>
                                {fileType === 'photo'
                                  ? <ImagePlus size={17} aria-hidden="true" />
                                  : <FileText size={17} aria-hidden="true" />}
                                <span className="document-item__name">{file.name}</span>
                                <span className="document-item__size">{formatFileSize(file.size)}</span>
                                <button
                                  aria-label={`Quitar ${file.name}`}
                                  className="remove-file-button"
                                  onClick={() => removeServiceDocument(value, id)}
                                  type="button"
                                >
                                  <Trash2 size={17} aria-hidden="true" />
                                </button>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )
                  })}
                </div>
              </fieldset>

              {selectedServices.length > 0 && (
                <section className="service-summary form-field form-field--full" aria-label="Resumen de trámites seleccionados">
                  <h3>Resumen de tu solicitud</h3>
                  <ul>
                    {selectedServices.map((serviceValue) => {
                      const service = serviceCatalog.find((item) => item.value === serviceValue)
                      const options = selectedPricingDetails.filter((item) => item.service === serviceValue)
                      return (
                        <li key={serviceValue}>
                          <strong>{service?.label}</strong>
                          {options.length > 0
                            ? <ul>{options.map((option) => (
                              <li key={`${option.group}-${option.option}`}>
                                {option.group}: {option.option} · {option.time} · {formatPrice(option)}
                              </li>
                            ))}</ul>
                            : <span>{service?.note ?? 'Selecciona las opciones de servicio que necesitas.'}</span>}
                        </li>
                      )
                    })}
                  </ul>
                  <p className="service-summary__total">
                    Total estimado: {formattedTotal}
                  </p>
                  {hasUnpricedSelection && (
                    <p className="service-summary__note">El total no incluye los conceptos marcados «Precio a consultar».</p>
                  )}
                  {hasCustomPricedServices && (
                    <p className="service-summary__note">Algunos trámites requieren cotización personalizada.</p>
                  )}
                </section>
              )}

              {selectedServices.includes('otros') && (
                <label className="form-field form-field--full">
                  <span>Describe tu trámite <span className="required-mark">*</span></span>
                  <textarea
                    name="other_service"
                    onChange={(event) => setOtherServiceDescription(event.target.value)}
                    placeholder="Escribe el trámite que necesitas."
                    rows="4"
                    required
                    value={otherServiceDescription}
                  />
                </label>
              )}

            </div>

            <div className="form-actions">
              <p><span className="required-mark">*</span> Selecciona al menos un trámite.</p>
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting
                  ? authToken ? 'Enviando solicitud...' : 'Creando cuenta y enviando...'
                  : authToken ? 'Enviar solicitud' : 'Crear cuenta y enviar solicitud'} <ArrowRight size={18} aria-hidden="true" />
              </button>
            </div>
            {submissionError && <p className="form-notice form-notice--error" role="alert">{submissionError}</p>}
          </form>
        )}

        {step === 'complete' && (
          <div className="application-form application-complete" role="status">
            <CheckCircle2 className="application-complete__icon" size={35} aria-hidden="true" />
            <div className="application-complete__content">
              <h3>Tus trámites quedaron guardados en la plataforma</h3>
              <p className="application-complete__label">Trámites solicitados</p>
              <ul className="application-complete__services">
                {selectedServices.map((serviceValue) => {
                  const service = serviceCatalog.find((item) => item.value === serviceValue)
                  const options = selectedPricingDetails.filter((item) => item.service === serviceValue)
                  return (
                    <li className="application-complete__service" key={serviceValue}>
                      <strong>{service?.label}</strong>
                      {options.length > 0
                        ? <ul className="application-complete__options">{options.map((option) => (
                          <li key={`${option.group}-${option.option}`}>
                            {option.group}: {option.option} · {option.time} · {formatPrice(option)}
                          </li>
                        ))}</ul>
                        : <span className="application-complete__description">{service?.note ?? 'Pendiente de cotización'}</span>}
                    </li>
                  )
                })}
              </ul>
              <div className="application-complete__total">
                <span>Total estimado</span>
                <strong>{formattedTotal}</strong>
                {(hasUnpricedSelection || hasCustomPricedServices) && (
                  <small>El total no incluye los conceptos cuyo precio debe confirmarse.</small>
                )}
              </div>
              <div className="application-complete__contact">
                <div>
                  <strong>Falta enviarlos por WhatsApp</strong>
                  <p>Abre WhatsApp, revisa el mensaje preparado y pulsa enviar para que podamos recibir tu consulta. Los tiempos y precios se confirmarán al revisarla.</p>
                </div>
                <a className="phone-contact__link" href={`https://wa.me/5358049659?text=${encodeURIComponent(whatsappMessage)}`} target="_blank" rel="noreferrer">
                  <MessageCircle size={17} aria-hidden="true" /> Abrir WhatsApp
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}


export default function ApplicationPage() {
  return (
    <main className="application-page">
      <header className="application-page__header">
        <a href="/" className="application-page__brand">
          <img src="/logo-lba.png" alt="" />
          <span>LB&amp;A Consulter</span>
        </a>
        <a href="/" className="application-page__back">Volver al inicio</a>
      </header>
      <ApplicationForm />
    </main>
  )
}
