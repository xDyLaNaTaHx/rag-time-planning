import { useState, type FormEvent, type KeyboardEvent } from 'react'

interface ItemListProps {
  title: string
  description: string
  items: string[]
  onChange: (items: string[]) => void
  placeholder: string
}

export function ItemList({
  title,
  description,
  items,
  onChange,
  placeholder,
}: ItemListProps) {
  const [draft, setDraft] = useState('')

  function addItem(event?: FormEvent) {
    event?.preventDefault()
    const value = draft.trim()
    if (!value) return
    onChange([...items, value])
    setDraft('')
  }

  function removeItem(index: number) {
    onChange(items.filter((_, i) => i !== index))
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter') {
      event.preventDefault()
      addItem()
    }
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>{title}</h2>
        <p>{description}</p>
      </header>

      <ul className="item-list">
        {items.length === 0 && (
          <li className="item-empty">Nothing added yet.</li>
        )}
        {items.map((item, index) => (
          <li key={`${item}-${index}`} className="item-row">
            <span>{item}</span>
            <button
              type="button"
              className="ghost-btn"
              aria-label={`Remove ${item}`}
              onClick={() => removeItem(index)}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>

      <form className="add-row" onSubmit={addItem}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          aria-label={`Add ${title.toLowerCase()}`}
        />
        <button type="submit" className="secondary-btn">
          Add
        </button>
      </form>
    </section>
  )
}
