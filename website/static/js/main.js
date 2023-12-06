console.log("Hello")
if (window.location.href.split('/')[3] == 'ledger-report'){
    tableBody = document.getElementById("dataTableBody");
    let ptnList = document.getElementById("partner-list");
    let namePtn = document.getElementById("namePtn");
    let overallDisplayer = document.getElementById("overall-displayer")
    let partnersArr = {};
    let show_and_hide_Arr = {};
    $(document).ready(function() {
        $('#date-range-picker').daterangepicker();
    });

    function reconcile(btn){
        if (btn.innerText == 'Show All Entries'){
            btn.innerText = "Only show unreconciled entries"
        }else{
            btn.innerText = "Show All Entries"
        }
    }
    function getShops(inp){
        dropperDiv = inp.nextElementSibling
        if (inp.value.length !== 0){
            dropperDiv.style.display = "";
        }else{
            dropperDiv.style.display = "none";
        }
        filter = inp.value.toUpperCase();
        let a = dropperDiv.getElementsByTagName("p");
        for (let i = 0; i < a.length; i++) {
            let txtValue = a[i].textContent || a[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
            a[i].style.display = "";
            } else {
            a[i].style.display = "none";
            }
        }
    }

    function assignShop(btn){
        if(btn.classList.contains("chooseOption")){
            console.log(btn.getAttribute("value"))
            btn.parentElement.previousElementSibling.previousElementSibling.value = btn.getAttribute("value")
            btn.parentElement.previousElementSibling.innerText = btn.innerText
        }else{
            let idd = btn.getAttribute('shopID')
            btn.parentElement.parentElement.parentElement.previousElementSibling.innerText = btn.innerText
            btn.parentElement.parentElement.parentElement.previousElementSibling.previousElementSibling.value = idd
            btn.parentElement.parentElement.parentElement.previousElementSibling.setAttribute('shopID',idd)
            console.log(btn.parentElement.parentElement.parentElement.previousElementSibling.previousElementSibling.value)
        }
    }

    function dateChange(btn){
        btn.parentElement.previousElementSibling.innerText = btn.innerText
    }
    function getData(btn,para){
        pay = document.getElementById('payCheckBox')
        recev = document.getElementById('recvCheckBox')
        post = document.getElementById('postCheckBox')
        draft = document.getElementById('draftCheckBox')
        rec = document.getElementById("recOrunrec").innerText.trim()
        bi = document.getElementById("bi").getAttribute("shopID")
        pc = document.getElementById("pc").getAttribute("shopID")
        own = document.getElementById("own").getAttribute("shopID").replace(/\//g, "~")
        ptn = document.getElementById("ptn").getAttribute("shopID").replace(/\//g, "~")
        shop = document.getElementById('shop').getAttribute("shopID")
        date = document.getElementById('changeDate')
        let rangeDate = dataForm = ""

        startDate = document.getElementById("start-dt")
        endDate = document.getElementById("end-dt")
        pay = document.getElementById("pay-receive")
        rec =  document.getElementById("entries")
        accStatus = document.getElementById("acc-status")
        bi = document.getElementById("unit")
        pjCode = document.getElementById("pj-code")
        shop = document.getElementById("shop")
        owner = document.getElementById("owner")
        partner = document.getElementById("partner")

        if (startDate.value == "" || endDate.value == ""){
            alert("Date must be specified")
        }else if (bi.value == ""){
            alert("Business Unit must be assigned..")
        }else if(shop.value == ''){
            alert("Shops must be assigned..")
        }else if(rec.value == ''){
            alert("Please Choose Entry Status..")
        }else if (pay.value == ''){
            alert("Report must be either payable or receiveable..")
        }else if (accStatus.value == ''){
            alert("Report must be either posted or unposted...")
        }else if (pjCode.value == ''){
            alert("Project Code must be chosen.If not specified ( chose no filter project code )")        
        }else if (owner.value == ''){
            alert("Owner must be chosen.If not specified ( chose no filter owner )")
        }else if (partner.value == ''){
            alert("Partner must be chosen.If not specified ( chose no filter partner )")
        }else if ((owner.value != "" && owner.value != 'False ') && (partner.value != "" && partner.value != 'False')){
            alert("Report must not be filtered with both partner and owner.....")
        }else{
            let blurr = document.getElementById("partnerTable")
            let spin = document.getElementById("spinner")
            spin.style.display = ""
            blurr.classList.add("demo")
            rangeDate = rangeDate.replace(/\//g, "~")
            dataForm = `${pay.value}@${rec.value}@${accStatus.value}@${bi.value}@${pjCode.value}@${shop.value}@${owner.value}@${partner.value}@${startDate.value}@${endDate.value}`
            console.log(dataForm)
            // dataForm = `${pay.checked}@${recev.checked}@${post.checked}@${draft.checked}@${rec}@${bi}@${pc}@${shop}@${own}@${ptn}@${rangeDate}`
            if (para == "normal"){
                tableBody.innerHTML = ""
                fetch(`/get-data-all/${dataForm}`)
                .then(response => response.json())
                .then(data => {
                    let overallInit , overallDb , overallCd , overallBal
                    overallInit = 0
                    overallDb = 0
                    overallCd = 0
                    overallBal = 0
                    Object.entries(data).forEach(([key, value]) => {
                        var modifiedStr = key.replace(/'/g, '"');
                        var ptn = JSON.parse(modifiedStr);
                        let total_db = parseFloat("0.00")
                        let total_cd = parseFloat("0.00")
                        let fstIniBal = parseFloat(ptn[2])
                        let clicker = value.length == 0 ? "" : "fun(this)";
                        overallInit += typeof(ptn[2]) == typeof(12) ? ptn[2] : Number(ptn[2].replace(/,/g,''))
                        overallDb += typeof(ptn[3]) == typeof(12) ? ptn[3] : Number(ptn[3].replace(/,/g,''))
                        overallCd += typeof(ptn[4]) == typeof(12) ? ptn[4] : Number(ptn[4].replace(/,/g,''))
                        overallBal += typeof(ptn[5]) == typeof(12) ? ptn[5] : Number(ptn[5].replace(/,/g,''))
                        test_html = `<tr onclick="${clicker}" dataAttr='parentRow'  id="${ptn[0]}">
                                        <td class="text-start" id="ptnName">${ptn[1]}</td>
                                        <td class="num text-end">${ptn[2].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K</td>
                                        <td class="num text-end">${ptn[3].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K</td>
                                        <td class="num text-end">${ptn[4].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K</td>
                                        <td class="num text-end">${ptn[5].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K</td>
                                    </tr>
                                    <tr hidden>
                                        <td colspan="6" style="padding: 0;margin: 0;">
                                            <table class="table table-hover partner-table" style="width: 100%;">
                                                <thead>
                                                    <tr>
                                                        <th class="text-start text-success" style="background-color: #EEEEEE;">Date</th>
                                                        <th class="text-start text-success" style="background-color: #EEEEEE;">JRNL</th>
                                                        <th class="text-start text-success" style="background-color: #EEEEEE;">Account</th>
                                                        <th class="text-start text-success" style="background-color: #EEEEEE;">Ref</th>
                                                        <th class="text-start text-success" style="background-color: #EEEEEE;">Due Date</th>
                                                        <th class="text-start text-success" style="background-color: #EEEEEE;">Matching</th>
                                                        <th class="text-end text-success" style="background-color: #EEEEEE;">Initial Balance</th>
                                                        <th class="text-end text-success" style="background-color: #EEEEEE;">Debit</th>
                                                        <th class="text-end text-success" style="background-color: #EEEEEE;">Credit</th>
                                                        <th class="text-end text-success" style="background-color: #EEEEEE;">Amount Currency</th>
                                                        <th class="text-end text-success" style="background-color: #EEEEEE;">Balance</th>
                                                    </tr>
                                                </thead>
                                                <tbody class="${ptn[0]}">
 
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>`
                                    partnersArr[ptn[1]] = ptn[0]
                                    show_and_hide_Arr[ptn[0]] = value
                                    tableBody.innerHTML += test_html
                    });
                    spin.style.display = "none"
                    blurr.classList.remove("demo")
                    
                    let dateShowDiv = document.getElementById("header-date")
                    dateShowDiv.innerText = rangeDate

                    overallDisplayer.children[1].innerText = `${overallInit.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K`
                    overallDisplayer.children[2].innerText = `${overallDb.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K`
                    overallDisplayer.children[3].innerText = `${overallCd.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K`
                    overallDisplayer.children[4].innerText = `${overallBal.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })} K`
                })
                .catch(error => {console.log(error)})
            }else if (para == "excel"){
                fetch(`/get-excel-partner/${dataForm}`)
                .then(response => response.blob())
                .then(blob => { 
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'PartnerLedger.xlsx';
                    a.click();
                    URL.revokeObjectURL(url);
                    spin.style.display = "none"
                    blurr.classList.remove("demo")
                })
                .catch(error => {console.log(error)})
            }else{
                fetch(`/get-pdf-partner/${dataForm}`)
                .then(response => response.blob())
                .then(blob => { 
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'PartnerLedger.pdf';
                    a.click();
                    URL.revokeObjectURL(url);
                    spin.style.display = "none"
                    blurr.classList.remove("demo")
                })
                .catch(error => {console.log(error)})
            }
        }
    }

    function fun(tableRow){
        if (tableRow.nextElementSibling.getAttribute('hidden') !== null){
            tableRow.nextElementSibling.removeAttribute('hidden')
            idd = tableRow.id
        tsubBody = tableRow.nextElementSibling.getElementsByClassName(idd)
        tsubBody[0].innerHTML = ""
            for (const dt of show_and_hide_Arr[idd]){
                tsubBody[0].innerHTML += ` <tr>
                                            <td>${dt[0]}</td>
                                            <td>${dt[1]}</td>
                                            <td>${dt[2]}</td>
                                            <td>${dt[3]}</td>
                                            <td>${dt[4]}</td>
                                            <td>${dt[5]}</td>
                                            <td>${dt[6]}</td>
                                            <td>${dt[7]}</td>
                                            <td>${dt[8].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</td>
                                            <td>${dt[9].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</td>
                                            <td>${dt[10].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</td>
                                            <td>${dt[11].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</td>
                                        </tr>`
            }
        }else{
            tableRow.nextElementSibling.setAttribute('hidden','')
        }
    }

    function fillPtn(list){
        namePtn.value = list.textContent
        ptnList.style.display = "none"
        list.parentElement.parentElement.nextElementSibling.children[0].setAttribute("id",list.id)
        list.parentElement.parentElement.nextElementSibling.children[1].setAttribute("id",list.id)
    }

    function showOnlyPtn(btn){
        rmvBTN = document.getElementById("removePtnFilter")
        rmvBTN.style.display = ""
        const specificRowId = btn.id;
        if (specificRowId.length != 0){
            const rows = document.querySelectorAll("#dataTableBody tr[dataAttr='parentRow']");
            for (const row of rows) {
                rowId = row.getAttribute("id")
                if (rowId === specificRowId) {
                    row.style.display = ""
                } else{
                    row.style.display = "none"
                }
            }
        }
    }

    function rmvPTN(){
        rmvBTN.style.display = "none"
        const rows = document.querySelectorAll("#dataTableBody tr[dataAttr='parentRow']");
            for (const row of rows) {
                row.style.display = ""
            }
    }

    function findPartners(inp){
        let tablePartnerRows = document.getElementById("dataTableBody")
        ptnList.style.display = ""
        ptnList.innerHTML = ""
        if (inp.value.trim() != ""){
            filter = inp.value.toUpperCase()
            for (let name in partnersArr){
                if (name.toUpperCase().indexOf(filter) > -1){
                    ptnList.innerHTML += `<li class="list-group-item" id="${partnersArr[name]}" onclick="fillPtn(this)">${name}</li>`
                }
            }
       
         }
    }
}else if(window.location.href.endsWith("/auth/")){
    console.log("Auth")
    document.cookie = 'code_id' + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = 'admin' + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}else if(window.location.href.endsWith("/admin/login") || window.location.href.endsWith("/admin/grant") || window.location.href.endsWith("/admin/delUser") ){
    document.cookie = 'code_id' + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = 'admin' + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
    modal.style.display = "none";
    }

    function openForm(idd){
        inp = modal.getElementsByTagName('input')
        inp[0].setAttribute('value',idd)
        modal.style.display = "block";
    }

    function grantAdmin(idd,bool){
        fetch(`/admin/grantAdmin/${idd}/${bool}`)
        .then(response => location.reload())
        .catch(e => console.log(e))
    }

}

function searchPartnerFromTable(inp){
    console.log(inp.value)
    let inputedText = inp.value.trim().toLowerCase()
    document.querySelectorAll("#dataTableBody tr[dataattr='parentRow']").forEach(trRow => {
        if (trRow.querySelector("#ptnName").textContent.trim().toLowerCase().includes(inputedText)){
            trRow.classList.remove("d-none")
        }else{
            trRow.classList.add("d-none")
        }
    })
}