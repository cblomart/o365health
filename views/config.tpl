% rebase('base.tpl', title='Office 365 health initial config')
<form method="post">
    <input type="hidden" name="csrf_token" value="{{csrf_token}}">
    <label for="tenant_id" class="control-label">Tenant ID</label>
    <div class="input-group">
        <input type="text" class="form-control" aria-label="Tenant ID" name="tenant_id" required>
    </div>
    <label for="client_id" class="control-label">Client ID</label>
    <div class="input-group">
        <input type="text" class="form-control" aria-label="Client ID" name="client_id" required>
    </div>
    <label for="client_secret" class="control-label">Client Secret</label>
    <div class="input-group">
        <input type="text" class="form-control" aria-label="Client Secret" name="client_secret" required>
    </div>
    <button type="submit" class="btn btn-default btn-circle btn-xl" disabled>
    <i class="fa fa-hdd"></i>
    </button>
</form>