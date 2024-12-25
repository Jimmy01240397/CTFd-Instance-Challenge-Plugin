CTFd._internal.challenge.data = undefined;

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function() {};

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.render = null;

function loadInfo() {
    if (window.t !== undefined) {
        clearInterval(window.t);
        window.t = undefined;
    }
    CTFd._internal.challenge.expiredat = undefined;
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = `/plugins/${CTFd._internal.challenge.data.plugin_name}/status/${challenge_id}`;
    CTFd.fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then((res) => {
        if (res.status === 200) {
            return res.json();
        }
        if (res.status === 404) {
            CTFd.lib.$('#instance-panel').html('<div class="card" style="width: 100%;">' +
                '<div class="card-body">' +
                '<h5 class="card-title">Instance Info</h5>' +
                '<button type="button" class="btn btn-primary card-link" id="instance-button-boot" ' +
                '        onclick="CTFd._internal.challenge.boot()">' +
                'Launch an instance' +
                '</button>' +
                '</div>' +
                '</div>');
        }
        return null;
    }).then((res) => {
        if (res == null)
            return;
        CTFd._internal.challenge.expiredat = new Date(res.expiredat);
        const fmt = new Intl.DateTimeFormat([], { dateStyle: 'medium', timeStyle: 'long' });
        CTFd.lib.$('#instance-panel').html(
            `<div class="card" style="width: 100%;">
                <div class="card-body">
                    <h5 class="card-title">Instance Info</h5>
                    <h6 class="card-subtitle mb-2 text-muted" id="instance-challenge-count-down">
                        Stopping at: ${fmt.format(CTFd._internal.challenge.expiredat)}
                    </h6>
                    <p id="user-access" class="card-text">
                        Access point: ${res.accesspoint}
                    </p>
                    <button type="button" class="btn btn-danger card-link" id="instance-button-destroy"
                            onclick="CTFd._internal.challenge.destroy()">
                        Destroy this instance
                    </button>
                </div>
            </div>`
        );

        function showAuto() {
            const now = new Date();
            const diffInMs = CTFd._internal.challenge.expiredat - now;
            if (diffInMs < 0) {
                loadInfo();
            }
        }
        window.t = setInterval(showAuto, 1000);
    });
};

CTFd._internal.challenge.postRender = loadInfo;

CTFd._internal.challenge.boot = function () {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = `/plugins/${CTFd._internal.challenge.data.plugin_name}/create/${challenge_id}`;
    CTFd.lib.$('#instance-button-boot')[0].innerHTML = "Waiting...";
    CTFd.lib.$('#instance-button-boot')[0].disabled = true;
    var params = {};
    CTFd.fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then((res) => {
        loadInfo();
    });
}

CTFd._internal.challenge.destroy = function () {
    var challenge_id = CTFd._internal.challenge.data.id;
    var url = `/plugins/${CTFd._internal.challenge.data.plugin_name}/destroy/${challenge_id}`;
    CTFd.lib.$('#instance-button-destroy')[0].innerHTML = "Waiting...";
    CTFd.lib.$('#instance-button-destroy')[0].disabled = true;
    var params = {};
    CTFd.fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then((res) => {
        loadInfo();
    });
}

CTFd._internal.challenge.submit = function(preview) {
  var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());
  var submission = CTFd.lib.$("#challenge-input").val();

  var body = {
    challenge_id: challenge_id,
    submission: submission
  };
  var params = {};
  if (preview) {
    params["preview"] = true;
  }

  return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
    if (response.status === 429) {
      // User was ratelimited but process response
      return response;
    }
    if (response.status === 403) {
      // User is not logged in or CTF is paused.
      return response;
    }
    return response;
  });
};
