class NotebookApp {
    constructor() {
        this.notes = [];
        this.currentNote = null;
        // Use relative path for production (nginx will proxy to backend)
        this.apiBaseUrl = '/api';
        
        this.initializeEventListeners();
        this.loadNotes();
    }

    async loadNotes() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/notes`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.notes = await response.json();
            this.renderNotesList();
        } catch (error) {
            console.error('Error loading notes:', error);
            alert('Failed to load notes. Please check if the backend is running.');
        }
    }

    async saveNote() {
        const title = document.getElementById('noteTitle').value;
        const content = document.getElementById('noteContent').value;

        try {
            if (this.currentNote.id) {
                // Update existing note
                const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            } else {
                // Create new note
                const response = await fetch(`${this.apiBaseUrl}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                this.currentNote.id = result.id;
            }
            
            await this.loadNotes();
        } catch (error) {
            console.error('Error saving note:', error);
            alert('Failed to save note. Please try again.');
        }
    }

    async deleteNote() {
        if (!this.currentNote?.id) return;

        if (confirm('Are you sure you want to delete this note?')) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/notes/${this.currentNote.id}`, {
                    method: 'DELETE'
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                this.currentNote = null;
                this.hideEditor();
                await this.loadNotes();
            } catch (error) {
                console.error('Error deleting note:', error);
                alert('Failed to delete note.');
            }
        }
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new NotebookApp();
});