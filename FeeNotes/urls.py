from django.urls import path
from .views import fee_notes, add_fee_note, mark_fee_note_as_paid, delete_fee_note, upload_fee_note, generate_fee_note_pdf, pdf_preview

urlpatterns = [
    path('', fee_notes, name='fee-notes'),
    path('add_fee_note/', add_fee_note, name='add_fee_note'),
    path('mark_fee_note_as_paid/<int:fee_note_id>', mark_fee_note_as_paid, name='mark_fee_note_as_paid'),
    path('delete_fee_note/<int:fee_note_id>', delete_fee_note, name='delete_fee_note'),
    path('upload_fee_note/<int:fee_note_id>', upload_fee_note, name='upload_fee_note'),
    path('generate_fee_note_pdf/<int:fee_note_id>', generate_fee_note_pdf, name='generate_fee_note_pdf'),
    path('pdf_preview/<int:fee_note_id>', pdf_preview, name='pdf_preview'),
]