from django.urls import reverse
import requests
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import Project, Chat
from projects.forms import ProjectForm, ChatForm

from notify_me import settings


@login_required
def index(request):
    # balance_error_text

    projects = Project.objects.filter(user_id=request.user.id)

    context = {"title": "Проекты", "projects": projects}

    return render(request, "projects/index.html", context)


@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(data=request.POST)
        if form.is_valid():
            system = form.cleaned_data["system"]
            provider = system.provider

            access_token = request.session.get(f"{provider}_access_token")

            if not access_token:
                request.session["saved_form_data"] = request.POST
                request.session["next_url"] = reverse("projects:add_project")

                return redirect("oauth:oauth_login", provider=provider)

            headers = {"Authorization": f"Bearer {access_token}"}

            start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            data = {
                "method": "add",
                "params": {
                    "Campaigns": [
                        {
                            "TimeZone": "Europe/Moscow",
                            "Name": request.POST.get("name"),
                            "StartDate": start_date,
                            "DailyBudget": {"Amount": 300000000, "Mode": "STANDARD"},
                            "TimeTargeting": {
                                "Schedule": {
                                    "Items": [
                                        "1,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                        "2,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                        "3,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                        "4,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                        "5,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                        "6,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                        "7,0,0,0,0,0,50,50,50,100,100,100,100,100,100,100,150,150,150,150,150,150,0,0,0",
                                    ]
                                },
                                "ConsiderWorkingWeekends": "NO",
                                "HolidaysSchedule": {
                                    "SuspendOnHolidays": "NO",
                                    "BidPercent": 50,
                                    "StartHour": 0,
                                    "EndHour": 23,
                                },
                            },
                            "TextCampaign": {
                                "BiddingStrategy": {
                                    "Search": {
                                        "BiddingStrategyType": "HIGHEST_POSITION"
                                    },
                                    "Network": {"BiddingStrategyType": "SERVING_OFF"},
                                },
                                "Settings": [
                                    {"Option": "ADD_TO_FAVORITES", "Value": "YES"}
                                ],
                            },
                        }
                    ]
                },
            }

            response = requests.post(
                f"https://{settings.YANDEX_DIRECT_DOMAIN}/json/v5/campaigns/",
                headers=headers,
                json=data,
            )

            if response.status_code == 200:
                campaign = response.json()
                campaign_id = campaign["result"]["AddResults"][0]["Id"]

                project = form.save(commit=False)
                project.user = request.user
                project.campaign_id = campaign_id
                project.save()

                return redirect("projects:index")
            else:
                form.non_field_errors = f"{response.status_code}: {response.text}"
    else:
        if "saved_form_data" in request.session:
            initial_data = request.session.pop("saved_form_data")

            request.method = "POST"
            request.POST = initial_data
            return add_project(request)
        else:
            form = ProjectForm()

    context = {"title": "Добавить проект", "form": form}

    return render(request, "projects/add_project.html", context)


@login_required
def chats(request, project_id):
    # send_comment_error_text

    project = get_object_or_404(Project, id=project_id, user_id=request.user.id)

    chats = project.chats.all()

    context = {
        "title": "Список чатов проекта",
        "project_id": project_id,
        "chats": chats,
    }

    return render(request, "projects/chats.html", context)


@login_required
def add_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    form = ChatForm(data=request.POST)
    if form.is_valid():
        chat = form.save(commit=False)
        chat.project = project
        chat.save()

        return redirect("projects:chats", project_id=project_id)
    else:
        chats = Chat.objects.filter(project_id=project_id)

        context = {
            "title": "Список чатов проекта",
            "project_id": project_id,
            "form": form,
            "chats": chats,
        }

        return render(request, "projects/chats.html", context)
