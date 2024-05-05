from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render, redirect
import requests
from carts.models import Cart, CartItem
from orders.models import Order
from store.models import Product
from account.forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from account.models import Account, UserProfile
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id
# verification email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password)
            user.phone_number = phone_number
            user.is_active = False
            user.save()

            # User activation
            current_site = get_current_site(request)
            mail_subject = 'Please Activate Your Account'
            message = render_to_string('account/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()
            # messages.success(request, "You are successfully registered!!")
            # return redirect('/user/login/?command=verification&email='+email)
            return render(request, "account/activation_sent.html", {"form": RegistrationForm})
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Link user to a cartItem
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []

                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # getting the cart item from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are log in.",
                             extra_tags='login_success')
            # Start Here we make the redirect system if the user finishes to authentificate himself
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        # Start Here we make the redirect system if the user finishes to authentificate himself
        else:
            messages.error(request, "Invalid login credentials",
                           extra_tags='login_error')
            return redirect('login')

    return render(request, 'account/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.",
                     extra_tags='login_success')
    return redirect('home')

# Account activation


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'Congratulation your account is activated!!', extra_tags='activate_success')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.',
                       extra_tags='activate_error')
        return redirect('register')


@login_required(login_url="login")
def dashboard(request):
    return render(request, 'account/dashboard/dashboard.html')


@login_required(login_url='login')
def edit_profile(request):
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request, 'Your profile has been updated.', extra_tags='edit_profile_success')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'account/dashboard/edit_profile.html', context)


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your password'
            message = render_to_string('user/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, "Password reset email has been sent to your email address!!",  extra_tags='pwdf_success')
            return redirect('login')
        else:
            messages.error(request, 'User does not exists',
                           extra_tags='pwdf_error')
            return redirect('forgotPassword')
    return render(request, 'account/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password',
                         extra_tags='pwdresetvalidate_success')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!',
                       extra_tags='pwdresetvalidate_error')
        return redirect('register')


def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['password2']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful!!",
                             extra_tags='pwdreset_success')
            return redirect('login')
        else:
            messages.error(request, 'Password reset successful',
                           extra_tags='pwdreset_error')
            return redirect('resetPassword')
    else:
        return render(request, 'account/resetPassword.html')


def tab_content(request):
    # Handle AJAX request here and return data accordingly
    tab_id = request.GET.get('tab_id')
    # Sample data, you should replace this with your data retrieval logic
    if tab_id == '1':
        data = {'content': 'Content for Tab 1'}
    elif tab_id == '2':
        data = {'content': 'Content for Tab 2'}
    else:
        data = {'content': 'Invalid Tab ID'}
    return JsonResponse(data)


@login_required(login_url='login')
def my_orders(request):
    current_user = request.user
    orders = Order.objects.filter(
        user=current_user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,

    }
    return render(request, 'account/dashboard/orders.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.Logout(request)
                messages.success(
                    request, 'Password Updated Successfully.', extra_tags='change_password_success')
                return redirect('change_password')
            else:
                messages.error(
                    request, 'Please enter valid current password', extra_tags='change_password_error')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'account/dashboard/change_password.html')
