<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $cc = $_POST['cc'];

    // Këtu mund të shtoni logjikën për të verifikuar kartat e kreditit duke përdorur API-në.
    $response = verifyCreditCards($cc);

    echo json_encode($response);
}

function verifyCreditCards($cc) {
    // Simulim i përgjigjes nga API i verifikimit të kartave
    $cards = explode("\n", trim($cc));
    $live = [];
    $die = [];
    $unknown = [];

    foreach ($cards as $card) {
        // Këtu mund të bëni thirrjen në API-në e verifikimit dhe të klasifikoni përgjigjen.
        $result = rand(0, 2); // 0 = aktive (live), 1 = joaktive (die), 2 = e panjohur (unknown)

        if ($result == 0) {
            $live[] = $card;
        } elseif ($result == 1) {
            $die[] = $card;
        } else {
            $unknown[] = $card;
        }
    }

    return [
        'success' => true,
        'live' => $live,
        'die' => $die,
        'unknown' => $unknown
    ];
}
?>
