console.log('🚀 Cloud Notebook Frontend Initialized');

class CloudNotebook {
    constructor() {
        this.notes = [];
        this.currentNote = null;
        this.initializeApp();
    }

    initializeApp() {
        console.log('🔧 Setting up application...');
        this.bindEvents();
        this.loadNotes();
    }

    bindEvents() {
        // Button events
        document.getElementById('newNoteBtn').addEventListener('click', () => this.createNote());
        document.getElementById('saveBtn').addEventListener('click', () => this.saveNote());
        document.getElementById('deleteBtn').addEventListener('click', () => this.deleteNote());
        
        // Input events for auto-save indicator
        document.getElementById('noteTitle').addEventListener('input', () => this.enableSave());
        document.getElementById('noteContent').addEventListener('input', () => this.enableSave());
        
        console.log('✅ All event listeners bound');
    }

    async loadNotes() {
        console.log('📡 Loading notes from API...');
        try {
            const response = await fetch('/api/notes');
            
            if (!response.ok) {
                throw new Error(`Failed to load notes: ${response.status} ${response.statusText}`);
            }
            
            this.notes = await response.json();
            console.log(`✅ Loaded ${this.notes.length} notes`);
            this.renderNotesList();
            
        } catch (error) {
            console.error('❌ Error loading notes:', error);
            this.showStatus('Error loading notes: ' + error.message, 'error');
            document.getElementById('notesList').innerHTML = 
                '<div class="error">Failed to load notes. Please refresh the page.</div>';
        }
    }

    renderNotesList() {
        const notesList = document.getElementById('notesList');
        
        if (this.notes.length === 0) {
            notesList.innerHTML = '<div class="no-notes">No notes yet. Create your first note!</div>';
            return;
        }

        let html = '';
        this.notes.forEach(note => {
            const isActive = this.currentNote && this.currentNote.id === note.id;
            html += `
                <div class="note-item ${isActive ? 'active' : ''}" data-note-id="${note.id}">
                    <strong>${this.escapeHtml(note.title || 'Untitled Note')}</strong>
                    <span class="note-preview">${this.escapeHtml(note.content ? note.content.substring(0, 60) + (note.content.length > 60 ? '...' : '') : 'Empty note')}</span>
                </div>
            `;
        });
        
        notesList.innerHTML = html;
        
        // Add click listeners to note items
        notesList.querySelectorAll('.note-item').forEach(item => {
            item.addEventListener('click', () => {
                const noteId = parseInt(item.dataset.noteId);
                const note = this.notes.find(n => n.id === noteId);
                if (note) {
                    this.selectNote(note);
                }
            });
        });
    }

    selectNote(note) {
        console.log('📝 Selecting note:', note.id);
        this.currentNote = note;
        
        // Update UI
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('noteEditor').style.display = 'block';
        document.getElementById('noteTitle').value = note.title || '';
        document.getElementById('noteContent').value = note.content || '';
        document.getElementById('deleteBtn').style.display = 'block';
        document.getElementById('saveBtn').disabled = true;
        
        // Update active state in notes list
        this.renderNotesList();
    }

    createNote() {
        console.log('🆕 Creating new note');
        this.currentNote = null;
        
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('noteEditor').style.display = 'block';
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        document.getElementById('deleteBtn').style.display = 'none';
        document.getElementById('saveBtn').disabled = true;
        
        // Clear active state in notes list
        this.renderNotesList();
        
        // Focus on title field
        document.getElementById('noteTitle').focus();
    }

    enableSave() {
        document.getElementById('saveBtn').disabled = false;
    }

    async saveNote() {
        const title = document.getElementById('noteTitle').value.trim() || 'Untitled Note';
        const content = document.getElementById('noteContent').value;
        
        if (!title && !content) {
            this.showStatus('Note cannot be empty', 'error');
            return;
        }

        console.log('💾 Saving note...');
        document.getElementById('saveBtn').disabled = true;
        document.getElementById('saveBtn').textContent = 'Saving...';

        try {
            let response, result;
            
            if (this.currentNote) {
                // Update existing note
                console.log('🔄 Updating note:', this.currentNote.id);
                response = await fetch(`/api/notes/${this.currentNote.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title, content })
                });
            } else {
                // Create new note
                console.log('🆕 Creating new note');
                response = await fetch('/api/notes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title, content })
                });
            }

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }

            result = await response.json();
            console.log('✅ Save successful:', result);
            
            this.showStatus(this.currentNote ? 'Note updated successfully!' : 'Note created successfully!', 'success');
            
            // Reload notes to get updated list
            await this.loadNotes();
            
            // If it was a new note, select it
            if (!this.currentNote && result.id) {
                const newNote = this.notes.find(n => n.id === result.id);
                if (newNote) {
                    this.selectNote(newNote);
                }
            }
            
        } catch (error) {
            console.error('❌ Error saving note:', error);
            this.showStatus('Error saving note: ' + error.message, 'error');
            document.getElementById('saveBtn').disabled = false;
        } finally {
            document.getElementById('saveBtn').textContent = 'Save';
        }
    }

    async deleteNote() {
        if (!this.currentNote) {
            return;
        }

        if (!confirm('Are you sure you want to delete this note? This action cannot be undone.')) {
            return;
        }

        console.log('🗑️ Deleting note:', this.currentNote.id);
        
        try {
            const response = await fetch(`/api/notes/${this.currentNote.id}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }

            console.log('✅ Delete successful');
            this.showStatus('Note deleted successfully!', 'success');
            
            // Clear editor and reload notes
            this.createNote();
            await this.loadNotes();
            
        } catch (error) {
            console.error('❌ Error deleting note:', error);
            this.showStatus('Error deleting note: ' + error.message, 'error');
        }
    }

    showStatus(message, type) {
        // Remove existing status message
        const existingStatus = document.getElementById('statusMessage');
        if (existingStatus) {
            existingStatus.remove();
        }

        // Create new status message
        const statusEl = document.createElement('div');
        statusEl.id = 'statusMessage';
        statusEl.className = `status-message status-${type}`;
        statusEl.textContent = message;
        
        document.body.appendChild(statusEl);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (statusEl.parentNode) {
                statusEl.remove();
            }
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM fully loaded, starting application...');
    window.cloudNotebook = new CloudNotebook();
});

// Handle potential errors
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});
