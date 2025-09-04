import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [step, setStep] = useState(1)
  const navigate = useNavigate()

  function sendOTP() {
    if (phone.length >= 10) {
      setStep(2)
      setTimeout(() => alert('Verification code sent (demo: 1234).'), 300)
    } else {
      alert('Enter a valid phone number')
    }
  }

  function verifyOTP() {
    if (otp === '1234') {
      navigate('/chat')
    } else {
      alert('Invalid code. Try 1234')
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Login</h2>
      {step === 1 && (
        <div>
          <div>
            <label>Phone</label>
            <input value={phone} onChange={e => setPhone(e.target.value)} />
          </div>
          <button onClick={sendOTP}>Send Code</button>
        </div>
      )}
      {step === 2 && (
        <div>
          <div>
            <label>Code</label>
            <input value={otp} onChange={e => setOtp(e.target.value)} />
          </div>
          <button onClick={verifyOTP}>Verify</button>
        </div>
      )}
    </div>
  )
}


