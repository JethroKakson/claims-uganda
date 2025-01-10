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
from django.http import HttpResponse, FileResponse
from django.utils.timezone import now
from io import BytesIO
from num2words import num2words
from django.contrib.humanize.templatetags.humanize import intcomma


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
            form.instance.total = float(total) + float(vat)
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
    font_path = 'gothic.ttf'
    
    if not os.path.isfile(font_path):
        font_path = None
    
    image = Image.open('note.jpg')
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    font_default = ImageFont.load_default()
    font_small = ImageFont.truetype(font_path, 30) if font_path else font_default
    font_medium = ImageFont.truetype(font_path, 40) if font_path else font_default
    font_amount = ImageFont.truetype(font_path, 60) if font_path else font_default
    font_large = ImageFont.truetype(font_path, 70) if font_path else font_default

    color = (0, 0, 0)

    # Draw texts
    draw.text((360, 900), 'M/S ' + fee_note.case.get_insurance_Company_display().upper(), font=font_medium, fill=color)
    draw.text((1700, 810), fee_note.case.reference_number, font=font_medium, fill=color)
    draw.text((560, 1130), fee_note.case.description.upper(), font=font_medium, fill=color)
    draw.text((560, 1240), 'M/S '+fee_note.case.client, font=font_medium, fill=color)
    draw.text((1275, 805), now().strftime("%Y-%m-%d"), font=font_medium, fill=color)

    words = num2words(fee_note.total, lang='en') + ' Ugandan Shillings'.strip(',')
    draw.text((800, 2625), words.lower(), font=font_small, fill=color)

    amounts = [
        fee_note.inspection_and_assessment_fee, fee_note.accommodation_fee,
        fee_note.out_of_office_allowance, fee_note.travel_and_assessment_fee,
        fee_note.photos, fee_note.value_added_tax, fee_note.total
    ]
    
    y_positions = [1500, 1650, 1790, 1930, 2050, 2150, 2250]
    for idx, y in enumerate(y_positions):
        if amounts[idx] > 0:
            draw.text((1120, y), f"{intcomma(int(amounts[idx]))}", font=font_amount, fill=color)
    buffer = BytesIO()
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(buffer, 'PDF')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="fee_note_{fee_note_id}.pdf"'

    return response



def pdf_preview(request, fee_note_id):
    fee_note = FeeNote.objects.get(id=fee_note_id)
    font_path = 'gothic.ttf'
    
    if not os.path.isfile(font_path):
        font_path = None
    
    image = Image.open('note.jpg')
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    font_default = ImageFont.load_default()
    font_small = ImageFont.truetype(font_path, 30) if font_path else font_default
    font_medium = ImageFont.truetype(font_path, 40) if font_path else font_default
    font_large = ImageFont.truetype(font_path, 70) if font_path else font_default
    font_amount = ImageFont.truetype(font_path, 60) if font_path else font_default

    color = (0, 0, 0)

    # Draw texts
    draw.text((360, 900), 'M/S '+fee_note.case.get_insurance_Company_display().upper(), font=font_medium, fill=color)
    draw.text((1700, 810), fee_note.case.reference_number, font=font_medium, fill=color)
    draw.text((560, 1130), fee_note.case.description.upper(), font=font_medium, fill=color)
    draw.text((560, 1240), 'M/S '+fee_note.case.client, font=font_medium, fill=color)
    draw.text((1275, 805), now().strftime("%Y-%m-%d"), font=font_medium, fill=color)

    words = num2words(fee_note.total, lang='en') + ' Ugandan Shillings'.strip(',')
    draw.text((800, 2625), words.lower(), font=font_small, fill=color)

    amounts = [
        fee_note.inspection_and_assessment_fee, fee_note.accommodation_fee,
        fee_note.out_of_office_allowance, fee_note.travel_and_assessment_fee,
        fee_note.photos, fee_note.value_added_tax, fee_note.total
    ]

    y_positions = [1500, 1650, 1790, 1930, 2050, 2150, 2250]
    for idx, y in enumerate(y_positions):
        if amounts[idx] > 0:
            draw.text((1120, y), f"{intcomma(int(amounts[idx]))}", font=font_amount, fill=color)
    
    # Save to BytesIO
    output = BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)

    response = HttpResponse(output.getvalue(), content_type="image/jpeg")
    response['Content-Disposition'] = f'inline; filename="fee_note_{fee_note_id}.jpg"'

    return response
