from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import FeeNote
from .forms import FeeNoteForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.signals import post_delete
from django.dispatch import receiver
from PIL import Image, ImageDraw, ImageFont
import os
from django.http import HttpResponse
from django.utils.timezone import now
from io import BytesIO


@receiver(post_delete, sender=FeeNote)
def delete_file(sender, instance, **kwargs):
    try:
        os.remove(instance.valid_fee_note.path)
    except:
        pass

    


@login_required
def fee_notes(request):
    form = FeeNoteForm()
    if request.user.staff.department == 'Assessors':
        form.fields['case'].queryset = form.fields['case'].queryset.filter(assessor=request.user.staff.assessor, fee_note=None)
        fee_notes = request.user.staff.assessor.fee_notes.all()
    else:
        fee_notes = FeeNote.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(fee_notes, 10)
    try:
        fee_notes = paginator.page(page)
    except PageNotAnInteger:
        fee_notes = paginator.page(1)
    except EmptyPage:
        fee_notes = paginator.page(paginator.num_pages)
    return render(request, 'fee_notes.html', {'form': form, 'fee_notes': fee_notes})


@login_required
def add_fee_note(request):
    if request.method == 'POST':
        form = FeeNoteForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            total = form.instance.inspection_and_assessment_fee + form.instance.accommodation_fee + form.instance.out_of_office_allowance + form.instance.travel_and_assessment_fee + form.instance.photos
            vat = 0.18*float(total)
            form.instance.total = float(total) - vat
            form.instance.value_added_tax = vat
            print(form.instance.total)
            form.save()
            form.instance.case.fee_note = form.instance
            form.instance.case.assessor.fee_notes.add(form.instance)
            form.instance.case.save()
            messages.success(request, 'Fee note added successfully.')
            return redirect('fee-notes')
    else:
        form = FeeNoteForm()
    return render(request, 'fee_notes.html', {'form': form})


def upload_fee_note(request, fee_note_id):
    fee_note = FeeNote.objects.get(id=fee_note_id)
    if request.method == 'POST':
        file = request.FILES['file']
        fee_note.valid_fee_note = file
        fee_note.save()
        messages.success(request, 'Fee note uploaded successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'fee-notes'))
    else:
        form = FeeNoteForm(instance=fee_note)
        return render(request, 'fee_notes.html', {'form': form})
            


@login_required
def mark_fee_note_as_paid(request, fee_note_id):
    fee_note = FeeNote.objects.get(id=fee_note_id)
    fee_note.status = 'Paid'
    fee_note.save()
    messages.success(request, 'Fee note marked as paid.')
    return redirect(request.META.get('HTTP_REFERER', 'fee-notes'))

    
@login_required
def delete_fee_note(request, fee_note_id):
    fee_note = FeeNote.objects.get(id=fee_note_id)
    fee_note.delete()
    messages.success(request, 'Fee note deleted successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'fee-notes'))


@login_required
def generate_fee_note_pdf(request, fee_note_id):
    fee_note = FeeNote.objects.get(id=fee_note_id)
    image = Image.open('note.jpg')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', 70) if 'arial.ttf' else ImageFont.load_default()
    color = (0, 0, 0)
    draw.text((360, 900), fee_note.case.get_insurance_Company_display(), font=font, fill=color)
    font = ImageFont.truetype('arial.ttf', 45) if 'arial.ttf' else ImageFont.load_default()
    draw.text((1265, 810), now().strftime("%Y-%m-%d"), font=font, fill=color)
    font = ImageFont.truetype('arial.ttf', 70) if 'arial.ttf' else ImageFont.load_default()
    amounts = [fee_note.inspection_and_assessment_fee, fee_note.accommodation_fee, fee_note.out_of_office_allowance, fee_note.travel_and_assessment_fee, fee_note.photos, fee_note.value_added_tax, fee_note.total]
    x_pos = 1120
    positions = [
        (x_pos, 1500),
        (x_pos, 1650),
        (x_pos, 1790),
        (x_pos, 1930),
        (x_pos, 2050),
        (x_pos, 2150),
        (x_pos, 2250)
    ]

    for position in positions:
        draw.text(position, f"{amounts[positions.index(position)]} UGX", font=font, fill=color)
    buffer = BytesIO()
    
    # Ensure the image is in RGB mode for PDF
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Save the image to the buffer as a PDF
    image.save(buffer, 'PDF')
    buffer.seek(0)  # Rewind the buffer to the beginning
    
    # Return the PDF as a response
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="fee_note_{fee_note_id}.pdf"'

    return response

