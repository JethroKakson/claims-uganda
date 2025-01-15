from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import FeeNote
from .forms import FeeNoteForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from PIL import Image, ImageDraw, ImageFont
import os
from django.http import HttpResponse, FileResponse
from django.utils.timezone import now
from io import BytesIO
from num2words import num2words
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q

@receiver(pre_save, sender=FeeNote)
def number_fee_note(sender, instance, **kwargs):
    fee_note = instance
    if not fee_note.pk:
        fee_notes = FeeNote.objects.filter(date_created__date__year=now().year).count()
        no = fee_notes + 1
        while True:
            try:
                FeeNote.objects.get(fee_note_number=no)
                no += 1
            except FeeNote.DoesNotExist:
                fee_note.fee_note_number = no
                break


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
    if request.GET.get('query'):
        query = request.GET.get('query')
        fee_notes = fee_notes.filter(Q(case__reference_number__icontains=query) | Q(case__insurance_Company__icontains=query) | Q(case__policy__icontains=query) | Q(case__client__icontains=query))
    page = request.GET.get('page', 1)
    paginator = Paginator(fee_notes, 10)
    try:
        fee_notes = paginator.page(page)
    except PageNotAnInteger:
        fee_notes = paginator.page(1)
    except EmptyPage:
        fee_notes = paginator.page(paginator.num_pages)
    return render(request, 'fee_notes.html', {'form': form, 'fee_notes': fee_notes, 'search': True if request.GET.get('query') else False, 'query': request.GET.get('query')})


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
    font_amount = ImageFont.truetype(font_path, 40) if font_path else font_default
    font_large = ImageFont.truetype(font_path, 70) if font_path else font_default
    # font_ref = ImageFont.truetype(font_path, 50) if font_path else font_default

    # font_path = ""  # Replace with the path to your downloaded font file
    # font_size = 50
    font_ref = ImageFont.truetype('italic.ttf', 60) if font_path else font_default

    color = (0, 0, 0)

    # Draw texts
    fee_note_ref = f"Pro. Inv/{str(fee_note.date_created.date().year)[2:]}/{'0'*(3-len(str(fee_note.fee_note_number)))+str(fee_note.fee_note_number)}"
    draw.rectangle((1800, 700, 2200, 780), fill=(255, 255, 255))
    draw.rectangle((1700, 920, 2100, 980), fill=(255, 255, 255))
    draw.text((1700, 915), str(fee_note.case.customer_reference), font=font_medium, fill=(0, 0, 0))
    draw.text((380, 1975), str(fee_note.travel_detail), font=font_medium, fill=(0, 0, 0))
    draw.text((1800, 700), fee_note_ref, font=font_ref, fill=(240, 128, 128))
    draw.text((360, 910), 'M/S ' + fee_note.case.get_insurance_Company_display().upper(), font=font_medium, fill=color)
    case_ref = fee_note.case.reference_number
    case_ref_parts = case_ref.split('/')
    if len(case_ref_parts) > 2:
        case_ref_parts[2] = case_ref_parts[2].zfill(3)
    case_ref = '/'.join(case_ref_parts)
    draw.text((1700, 810), case_ref, font=font_medium, fill=color)
    draw.text((560, 1125), 'BEING PROFFESSIONAL FEES FOR SERVICES RENDERED ON ACCOUNT OF: \n'+fee_note.case.description.upper(), font=font_medium, fill=color)
    draw.text((560, 1245), 'M/S '+fee_note.case.client.upper(), font=font_medium, fill=color)
    draw.text((1275, 805), now().strftime("%d/%m/%Y"), font=font_medium, fill=color)

    words = num2words(fee_note.total, lang='en') + ' Ugandan Shillings'
    words_list = words.strip(',').split()
    if len(words_list) > 8:
        words = words_list
        first_line = ' '.join(words[:8])
        second_line = ' '.join(words[8:])
        draw.text((800, 2628), first_line[0].upper() + first_line[1:].lower(), font=font_medium, fill=color)
        draw.text((800, 2720), second_line[0] + second_line[1:], font=font_medium, fill=color)
    else:
        draw.text((800, 2625), words[0].upper() + words[1:].lower(), font=font_medium, fill=color)

    amounts = [
        fee_note.inspection_and_assessment_fee, fee_note.accommodation_fee,
        fee_note.out_of_office_allowance, fee_note.travel_and_assessment_fee,
        fee_note.photos, fee_note.value_added_tax, fee_note.total
    ]

    y_positions = [1500, 1650, 1790, 1930, 2050, 2150, 2250]
    for idx, y in enumerate(y_positions):
        if amounts[idx] > 0:
            draw.text((1250, y), f"{intcomma(int(amounts[idx]))}", font=font_amount, fill=color)
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
    font_amount = ImageFont.truetype(font_path, 40) if font_path else font_default
    font_large = ImageFont.truetype(font_path, 70) if font_path else font_default
    # font_ref = ImageFont.truetype(font_path, 50) if font_path else font_default
    font_ref = ImageFont.truetype('italic.ttf', 60) if font_path else font_default

    color = (0, 0, 0)

    # Draw texts
    fee_note_ref = f"Pro. Inv/{str(fee_note.date_created.date().year)[2:]}/{'0'*(3-len(str(fee_note.fee_note_number)))+str(fee_note.fee_note_number)}"
    draw.rectangle((1800, 700, 2200, 780), fill=(255, 255, 255))
    draw.rectangle((1700, 920, 2100, 980), fill=(255, 255, 255))
    draw.text((1700, 915), str(fee_note.case.customer_reference), font=font_medium, fill=(0, 0, 0))
    draw.text((380, 1975), str(fee_note.travel_detail), font=font_medium, fill=(0, 0, 0))
    draw.text((1800, 700), fee_note_ref, font=font_ref, fill=(240, 128, 128))
    draw.text((360, 910), 'M/S ' + fee_note.case.get_insurance_Company_display().upper(), font=font_medium, fill=color)
    case_ref = fee_note.case.reference_number
    case_ref_parts = case_ref.split('/')
    if len(case_ref_parts) > 2:
        case_ref_parts[2] = case_ref_parts[2].zfill(3)
    case_ref = '/'.join(case_ref_parts)
    draw.text((1700, 810), case_ref, font=font_medium, fill=color)
    draw.text((560, 1125), 'BEING PROFFESSIONAL FEES FOR SERVICES RENDERED ON ACCOUNT OF: \n'+fee_note.case.description.upper(), font=font_medium, fill=color)
    draw.text((560, 1245), 'M/S '+fee_note.case.client.upper(), font=font_medium, fill=color)
    draw.text((1275, 805), now().strftime("%d/%m/%Y"), font=font_medium, fill=color)

    words = num2words(fee_note.total, lang='en') + ' Ugandan Shillings'
    words_list = words.strip(',').split()
    if len(words_list) > 8:
        words = words_list
        first_line = ' '.join(words[:8])
        second_line = ' '.join(words[8:])
        draw.text((800, 2628), first_line[0].upper() + first_line[1:].lower(), font=font_medium, fill=color)
        draw.text((800, 2720), second_line[0].upper() + second_line[1:].lower(), font=font_medium, fill=color)
    else:
        draw.text((800, 2625), words[0].upper() + words[1:].lower(), font=font_medium, fill=color)

    amounts = [
        fee_note.inspection_and_assessment_fee, fee_note.accommodation_fee,
        fee_note.out_of_office_allowance, fee_note.travel_and_assessment_fee,
        fee_note.photos, fee_note.value_added_tax, fee_note.total
    ]

    y_positions = [1500, 1650, 1790, 1930, 2050, 2150, 2250]
    for idx, y in enumerate(y_positions):
        if amounts[idx] > 0:
            draw.text((1250, y), f"{intcomma(int(amounts[idx]))}", font=font_amount, fill=color)
    output = BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)

    response = HttpResponse(output.getvalue(), content_type="image/jpeg")
    response['Content-Disposition'] = f'inline; filename="fee_note_{fee_note_id}.jpg"'

    return response
