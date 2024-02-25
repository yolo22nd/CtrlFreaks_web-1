from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from schedule.serializers import *
from base.models import *
from base.serializers import *

# Create your views here.


class createEvent(APIView):
    def post(self, request):
        data = request.data.copy()
        # data['user'] = user.id  # Add the user id to the data

        # data["committee"]=Committee.objects.filter(name=request.data["committee_name"])
        # del data["committee_name"]
        # data["venue"]=Venue.objects.filter(name=request.data["venue_name"])
        # del data["venue_name"]
        serializer = EventsSerializer(data=request.data)
        event_name = request.data.get('name')
        # booking_data = {
        #     'date' : request.data.get('date'),
        #     'time' : request.data.get('time'),
        #     'committee' : request.data.get('committee'),
        #     'venue' : request.data.get('venue'),
        #     'event' : 
        # }

        event_name = request.data.get('name')
        if serializer.is_valid():
            try:
                serializer.save()
                principle = Faculty.objects.get(is_principle=True)
                hod = Faculty.objects.get(is_hod=True)
                mentor = Faculty.objects.get(is_mentor=True)
                dean = Faculty.objects.get(is_dean=True)
                print(principle, hod, mentor, dean)
                
                email_send(principle.email, principle.fac_id, event_name, request.data)
                email_send(hod.email, hod.fac_id, event_name, request.data)
                email_send(mentor.email, mentor.fac_id, event_name, request.data)
                email_send(dean.email, dean.fac_id, event_name, request.data)

                return Response({'message' : "Event booked successfully"})
            except Exception as e:
                print(f'errors : {e}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Sending approval email
def email_send(email, fac_id, event_name, event_data):
    subject = 'click the link to approve the event'
    message = f'{event_data}\nClick on the link to approve this event http://127.0.0.1:8000/events/approval/{event_name}/{fac_id}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


# Verifying the email
def email_approval(request, event, fac_id):
    faculty_obj = get_object_or_404(Faculty, fac_id=fac_id)
       
    event_obj = Event.objects.get(name=event)
    # booking = Booking.objects.get(event=event_obj)
    booking, created = Booking.objects.get_or_create(
        date=event_obj.date, 
        time=event_obj.time,
        venue=event_obj.venue,  
        committee=event_obj.committee, 
        event=event_obj)

    if faculty_obj.is_principle == True:
        if not booking.is_approved_pri:
            booking.is_approved_pri = True
            booking.save()
            return JsonResponse({'message' : 'Approved by principle'})
    
    if faculty_obj.is_hod == True:
        if not booking.is_approved_hod:
            booking.is_approved_hod = True
            booking.save()
            return JsonResponse({'message' : 'Approved by hod'})

    if faculty_obj.is_mentor == True:
        if not booking.is_approved_mentor:
            booking.is_approved_mentor = True
            booking.save()
            return JsonResponse({'message' : 'Approved by mentor'})
        
    if faculty_obj.is_dean == True:
        if not booking.is_approved_dean:
            booking.is_approved_dean = True
            booking.save()
            return JsonResponse({'message' : 'Approved by dean'})
    
    # if not faculty_obj.is_verified:
    #     user_obj.is_verified = True
    #     user_obj.save()
    #     print(user_obj)
    #     return JsonResponse({'message' : 'verified'})
        

        #add condition for all approve and set it true
    return JsonResponse({'message' : 'Event is already approved'})




class DisplayEventStudentApproved(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_approved=True)
    serializer_class = EventSerializerAll

class DisplayEventStudentRejected(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_rejected=True)
    serializer_class = EventSerializerAll

class DisplayEventStudentPrevious(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_approved=False)
    serializer_class = EventSerializerAll


class DisplayEventStudentPending(viewsets.ViewSet):
    serializer_class = EventSerializerAll

    def list(self, request):
        fac_id = request.data.get('fac_id')
        event_id = request.data.get('event_id')

        try:
            faculty_obj = Faculty.objects.get(fac_id=fac_id)
            event_obj = Event.objects.get(id=event_id)
            booking_obj = Booking.objects.get(event=event_obj)

            event_list = []

            if faculty_obj.is_principle:
                booking_queryset = Booking.objects.filter(is_approved_pri=False)
                event_list = [booking.event for booking in booking_queryset]
            elif faculty_obj.is_hod:
                booking_queryset = Booking.objects.filter(is_approved_hod=False)
                event_list = [booking.event for booking in booking_queryset]
            elif faculty_obj.is_mentor:
                booking_queryset = Booking.objects.filter(is_approved_mentor=False)
                event_list = [booking.event for booking in booking_queryset]
            elif faculty_obj.is_dean:
                booking_queryset = Booking.objects.filter(is_approved_dean=False)
                event_list = [booking.event for booking in booking_queryset]

            return Response({'event_list': event_list})
        except (Faculty.DoesNotExist, Event.DoesNotExist, Booking.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    queryset = Event.objects.filter(is_rejected=False , is_approved=False)
    serializer_class = EventSerializerAll


class DisplayEvent(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializerAll


class DispDelEvent(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class DisplayCommittee(viewsets.ModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer

   
class DisplayStudent(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class DisplayFaculty(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    
class DisplayVenue(viewsets.ModelViewSet):

    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


class Registration(APIView):
    def post(self, request):
        try:
            new_member_rollno = request.data.get('rollno')
            event_id = request.data.get('event_id')
            event_obj = Event.objects.get(id=event_id)
            student_obj = Student.objects.get(rollno=new_member_rollno)
            existing_members = event_obj.regi_members

            if existing_members:
                updated_members = f"{existing_members}, {new_member_rollno}"
            else:
                updated_members = new_member_rollno

            event_obj.regi_members = updated_members
            event_obj.save()
            subject = f'{event_obj.name} Registration'
            message = f'You are registered for {event_obj.name} successfully\nFollowing are the details of the event\n{event_obj}'
            student_email = student_obj.email
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject, message, email_from, [student_email])
            return JsonResponse({'message': 'Member registered successfully'}, status=status.HTTP_201_CREATED)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)